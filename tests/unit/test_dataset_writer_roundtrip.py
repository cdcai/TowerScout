"""Exercise actual writer archives across restore generations and legacy flags."""
import io
import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image
import pytest
import towerscout


@pytest.fixture
def writer(tmp_path, monkeypatch):
    fresh = tmp_path / 'fresh'
    fresh.mkdir()
    exports = tmp_path / 'exports'
    exports.mkdir()
    sequence = itertools.count()
    def stage():
        target = tmp_path / f'restored-{next(sequence)}'
        target.mkdir()
        return str(target)
    monkeypatch.setattr(towerscout, '_make_session_tmpdir', stage)
    monkeypatch.setattr(towerscout, 'get_temp_dir', lambda: exports)
    monkeypatch.setattr(towerscout.rate_limiter, 'is_allowed', lambda *a, **k: True)
    def offline(**kwargs):
        raise RuntimeError('synthetic offline geocoder')
    monkeypatch.setattr(towerscout, 'create_geocoding_service', offline)
    client = towerscout.app.test_client()
    tile_id = 0
    def seed(size, meta, image_format='JPEG', index=0):
        nonlocal tile_id
        tile_id = index
        filename = fresh / 'tile.jpg'
        with Image.new('RGB', size, 'white') as image:
            image.save(filename, format=image_format)
        tiles = [dict(index=index, filename=str(filename), labelfilename=str(fresh/'tile.txt'),
                      metadata='synthetic', detections=['0 0.15 0.25 0.1 0.1\n'])]
        rows = [dict(id=index, class_name='tile', x1=0, x2=1, y1=1, y2=0, conf=1, **{'class':1}),
                dict(tile=index,id_in_tile=0,class_name='ct',x1=.1,x2=.2,y1=.3,y2=.2,
                     conf=.9,inside=False,selected=True, **{'class':0})]
        with client.session_transaction() as state:
            state.update(tmpdirname=str(fresh),metadata=meta,detections=tiles,results=json.dumps(rows))
        return filename.read_bytes()
    def export(include=None, additions=None):
        if include is None:
            include = [dict(tile=tile_id,detection=0)]
        response = client.post('/getdataset',data={'include':json.dumps(include),
                               'additions':json.dumps(additions or [])})
        assert response.status_code == 200
        payload = response.get_data()
        response.close()
        return payload
    def restore(payload):
        return client.post('/uploaddataset',data={'dataset':(io.BytesIO(payload),'dataset.zip')})
    return client, seed, export, restore


def inspect_archive(payload):
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        xml = ET.fromstring(archive.read(next(n for n in names if n.endswith('/tile.xml'))))
        return dict(names=names, xml=xml,
                    image=archive.read(next(n for n in names if n.endswith('/tile.jpg'))),
                    labels=archive.read(next(n for n in names if n.endswith('/tile.txt'))),
                    contents=json.loads(archive.read(next(n for n in names if n.endswith('/contents.txt')))))


def rewrite_archive(payload, transform=None, extra=()):
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(payload)) as source, zipfile.ZipFile(output,'w') as target:
        for entry in source.infolist():
            data = source.read(entry)
            if transform:
                data = transform(entry.filename,data)
            target.writestr(entry,data)
        for name, data in extra:
            target.writestr(name,data)
    return output.getvalue()


def assert_xml_size_and_ml_box(xml, size):
    width, height = size
    assert (int(xml.findtext('size/width')),int(xml.findtext('size/height'))) == size
    box = xml.find('object/bndbox')
    assert int(box.findtext('xmin')) == int((.15-.05)*width)
    assert int(box.findtext('xmax')) == int((.15+.05)*width)
    assert int(box.findtext('ymin')) == int((.25-.05)*height)
    assert int(box.findtext('ymax')) == int((.25+.05)*height)


def test_actual_writer_readme_survives_repeated_restore(writer):
    _,seed,export,restore=writer
    seed((1280,1280),False)
    for _ in range(3):
        payload=export()
        assert restore(payload).status_code==200


@pytest.mark.parametrize('meta',[False,True])
@pytest.mark.parametrize('legacy',[False,True])
@pytest.mark.parametrize('size,image_format',[((1280,1280),'JPEG'),((640,640),'PNG'),((640,320),'TIFF')])
def test_actual_writer_multigeneration_roundtrip(writer,meta,legacy,size,image_format):
    client,seed,export,restore = writer
    image = seed(size,meta,image_format,index=0 if legacy else 7)
    for generation in range(3):
        payload = export()
        data = inspect_archive(payload)
        assert [n for n in data['names'] if n.endswith('README.txt')] == ['README.txt']
        assert data['image'] == image
        assert data['labels'].decode().splitlines() == ['0 0.15 0.25 0.1 0.1']
        assert data['contents'][2] is (not meta)
        assert_xml_size_and_ml_box(data['xml'],size)
        if legacy and generation == 0:
            def legacy_contents(name,raw):
                if name.endswith('/contents.txt'):
                    contents=json.loads(raw)
                    del contents[1][0]['id']
                    return json.dumps(contents).encode()
                return raw
            payload=rewrite_archive(payload,legacy_contents)
        response=restore(payload)
        assert response.status_code == 200
        with client.session_transaction() as state:
            assert state['metadata'] is meta
            assert not (Path(state['tmpdirname'])/'README.txt').exists()


@pytest.mark.parametrize('size',[(1280,1280),(640,640),(640,320)])
@pytest.mark.parametrize('meta',[False,True])
def test_historical_reexport_duplicate_readme_and_flipped_flag(writer,size,meta):
    client,seed,export,restore=writer
    image=seed(size,meta)
    first=export()
    stem=next(n for n in inspect_archive(first)['names'] if n.endswith('/contents.txt')).split('/')[0]
    def old_reexport_flag(name,raw):
        if name.endswith('/contents.txt'):
            data=json.loads(raw)
            data[2]=not data[2]
            return json.dumps(data).encode()
        return raw
    historical=rewrite_archive(first,old_reexport_flag,[(f'{stem}/empty/README.txt',b'Historical README')])
    assert restore(historical).status_code == 200
    for _ in range(2):
        payload=export()
        data=inspect_archive(payload)
        assert data['image']==image
        assert_xml_size_and_ml_box(data['xml'],size)
        assert [n for n in data['names'] if n.endswith('README.txt')]==['README.txt']
        assert restore(payload).status_code == 200


@pytest.mark.parametrize('size',[(1280,1280),(640,320)])
def test_manual_xml_uses_image_dimensions(writer,size):
    _,seed,export,_=writer
    seed(size,True)
    data=inspect_archive(export(include=[],additions=[dict(tile=0,centerx=.5,centery=.5,w=.2,h=.2,inside=False)]))
    xml=data['xml']
    assert (int(xml.findtext('size/width')),int(xml.findtext('size/height')))==size
    box=xml.find('object/bndbox')
    assert [int(box.findtext(k)) for k in ('xmin','xmax','ymin','ymax')]==[
        int(.4*size[0]),int(.6*size[0]),int(.4*size[1]),int(.6*size[1])]
    assert data['contents'][1][-1]['inside'] is False


@pytest.mark.parametrize('index',[False,0.0,True,1.0])
def test_invalid_index_that_aliases_real_label_stays_unselected(writer,index):
    client,seed,export,_=writer
    seed((8,8),False)
    with client.session_transaction() as state:
        state['detections'][0]['detections'].append('0 0.5 0.5 0.2 0.2\n')
        rows=json.loads(state['results'])
        rows.append(dict(rows[1],id_in_tile=1))
        state['results']=json.dumps(rows)
    data=inspect_archive(export(include=[dict(tile=0,detection=index)]))
    assert data['labels']==b'' and data['xml'].findall('object')==[]
    assert all(not r['selected'] for r in data['contents'][1][1:])


@pytest.mark.parametrize('member',['fresh/empty/tile.jpg','fresh/empty/contents.txt','../README.txt'])
def test_readme_compatibility_does_not_allow_other_collisions(writer,member):
    client,seed,export,restore=writer
    image=seed((8,8),False)
    original=export()
    with client.session_transaction() as state:
        previous=state['tmpdirname']
    response=restore(rewrite_archive(original,extra=[(member,b'conflicting')]))
    assert response.status_code==400
    with client.session_transaction() as state:
        assert state['tmpdirname']==previous
        assert Path(state['detections'][0]['filename']).read_bytes()==image


@pytest.mark.parametrize('limit',['MAX_DATASET_MEMBER_BYTES','MAX_DATASET_EXPANDED_BYTES','MAX_DATASET_MEMBERS'])
def test_ignored_readme_remains_subject_to_archive_budgets(writer,monkeypatch,limit):
    client,seed,export,restore=writer
    seed((8,8),False)
    payload=export()
    # Other members fit; including the ignored README is what exceeds the budget.
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        others=[i for i in archive.infolist() if i.filename!='README.txt']
        cap={'MAX_DATASET_MEMBER_BYTES':max(i.file_size for i in others)+1,
             'MAX_DATASET_EXPANDED_BYTES':sum(i.file_size for i in others)+1,
             'MAX_DATASET_MEMBERS':len(others)}[limit]
        if limit=='MAX_DATASET_MEMBER_BYTES':
            assert archive.getinfo('README.txt').file_size>cap
    monkeypatch.setattr(towerscout,limit,cap)
    with client.session_transaction() as state:
        previous=state['tmpdirname']
    assert restore(payload).status_code==400
    with client.session_transaction() as state:
        assert state['tmpdirname']==previous


def test_metadata_budget_is_checked_before_member_reads(writer,monkeypatch):
    _,seed,export,restore=writer
    seed((8,8),False)
    payload=export()
    monkeypatch.setattr(towerscout,'MAX_DATASET_METADATA_BYTES',32)
    reads=[]
    original=towerscout.zipfile.ZipFile.open
    def observe(self,*args,**kwargs):
        reads.append(str(args[0]))
        return original(self,*args,**kwargs)
    monkeypatch.setattr(towerscout.zipfile.ZipFile,'open',observe)
    response=restore(payload)
    assert response.status_code==400 and 'metadata' in response.json['error'].lower()
    assert reads==[], 'Oversized JSON must be rejected before reading any ZIP member'
