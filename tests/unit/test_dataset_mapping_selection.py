"""Real archive regressions for restore ownership and stable export selection."""
import copy
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image
import pytest
import towerscout


LABEL = '0 0.5 0.5 0.1 0.1\n'


def image_bytes(format='JPEG'):
    stream = io.BytesIO()
    with Image.new('RGB', (8, 8), 'white') as image:
        image.save(stream, format=format)
    return stream.getvalue()


def dataset(ids=(7, 21), labels=None):
    labels = labels or [[LABEL], [LABEL]]
    tiles, results = [], []
    for index, tile_id in enumerate(ids):
        tiles.append(dict(index=tile_id, filename=f'old/tile{index}.jpg', detections=labels[index]))
        results.append(dict(id=tile_id, class_name='tile', x1=index, x2=index+1,
                            y1=2, y2=1, conf=1, **{'class': 1}))
    for index, tile in enumerate(tiles):
        for label_index in range(len(tile['detections'])):
            results.append(dict(tile=tile['index'], id_in_tile=label_index, class_name='ct',
                                x1=index+.4, x2=index+.5, y1=1.5, y2=1.4,
                                conf=.8, selected=True, inside=False, **{'class': 0}))
    return [tiles, results, False]


def archive(data, entries=None):
    entries = entries if entries is not None else {
        'old/train/images/tile0.jpg': image_bytes(),
        'old/train/images/tile1.jpg': image_bytes(),
    }
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as z:
        for name, content in entries.items():
            z.writestr(name, content)
        z.writestr('contents.txt', json.dumps(data))
    stream.seek(0)
    return stream


@pytest.fixture
def review(tmp_path, monkeypatch):
    staging, previous, exports = (tmp_path / name for name in ('staging', 'previous', 'exports'))
    for directory in (staging, previous, exports):
        directory.mkdir()
    (previous / 'keep.jpg').write_bytes(image_bytes())
    monkeypatch.setattr(towerscout, '_make_session_tmpdir', lambda: str(staging))
    monkeypatch.setattr(towerscout, 'get_temp_dir', lambda: exports)
    monkeypatch.setattr(towerscout.rate_limiter, 'is_allowed', lambda *a, **k: True)
    client = towerscout.app.test_client()
    with client.session_transaction() as state:
        state.update(tmpdirname=str(previous), results='previous', detections=['previous'], metadata=True)
    return client, staging, previous


@pytest.mark.parametrize('case', ['missing', 'metadata', 'duplicate', 'derived-label',
    'reserved-contents', 'reserved-readme', 'case-alias', 'directory', 'xml-directory', 'fake-jpeg', 'unsupported-format'])
def test_invalid_tile_mapping_preserves_previous_review(review, case):
    client, staging, previous = review
    data = dataset()
    entries = {'old/train/images/tile0.jpg': image_bytes(), 'old/train/images/tile1.jpg': image_bytes()}
    if case == 'missing':
        data[0][0]['filename'] = 'old/missing.jpg'
    elif case == 'metadata':
        data[0][0]['filename'] = 'old/contents.txt'
    elif case == 'duplicate':
        data[0][1]['filename'] = data[0][0]['filename']
    elif case == 'derived-label':
        data[0][1]['filename'] = 'old/tile0.png'
        entries['old/train/images/tile0.png'] = image_bytes('PNG')
    elif case.startswith('reserved-'):
        name = 'contents' if case == 'reserved-contents' else 'README'
        data[0][0]['filename'] = f'old/{name}.jpg'
        entries[f'old/train/images/{name}.jpg'] = image_bytes()
    elif case == 'case-alias':
        data[0][1]['filename'] = 'old/TILE0.JPG'
        entries['old/train/images/TILE0.JPG'] = image_bytes()
    elif case == 'directory':
        del entries['old/train/images/tile0.jpg']
        entries['old/train/images/tile0.jpg/child'] = b'not an image'
    elif case == 'xml-directory':
        entries['old/train/images/tile0.xml/child'] = b'not a label output'
    elif case == 'fake-jpeg':
        entries['old/train/images/tile0.jpg'] = b'not an image'
    elif case == 'unsupported-format':
        entries['old/train/images/tile0.jpg'] = image_bytes('GIF')
    response = client.post('/uploaddataset', data={'dataset': (archive(data, entries), 'dataset.zip')})
    assert response.status_code == 400
    assert not staging.exists()
    assert (previous / 'keep.jpg').read_bytes() == image_bytes()
    with client.session_transaction() as state:
        assert state['results'] == 'previous' and state['detections'] == ['previous']
        assert state['tmpdirname'] == str(previous) and state['metadata'] is True


@pytest.mark.parametrize('legacy', [False, True])
@pytest.mark.parametrize('selected', [[], [(0, 0)], [(0, 1)], [(1, 0)], [(0, 0), (1, 0)]])
def test_restore_and_export_equal_labels_use_exact_references(review, monkeypatch, legacy, selected):
    client, staging, previous = review
    ids = (0, 1) if legacy else (7, 21)
    data = dataset(ids, [[LABEL, LABEL], [LABEL]])
    if legacy:
        for result in data[1][:2]:
            del result['id']
        data[0][0]['filename'] = r'C:\old\tile0.jpg'
    response = client.post('/uploaddataset', data={'dataset': (archive(data), 'dataset.zip')})
    assert response.status_code == 200
    assert not previous.exists()
    include = [{'tile': ids[tile], 'detection': detection} for tile, detection in selected]
    # No legacy absolute id is needed: noncontiguous stable tile ids suffice.
    response = client.post('/getdataset', data={'include': json.dumps(include), 'additions': '[]'})
    assert response.status_code == 200
    payload = response.get_data()
    response.close()
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        names = z.namelist()
        for tile in (0, 1):
            count = sum(t == tile for t, _ in selected)
            label_name = next(n for n in names if n.endswith(f'/tile{tile}.txt'))
            xml_name = next(n for n in names if n.endswith(f'/tile{tile}.xml'))
            image_name = next(n for n in names if n.endswith(f'/tile{tile}.jpg'))
            assert z.read(label_name).decode().splitlines() == [LABEL.strip()] * count
            assert len(ET.fromstring(z.read(xml_name)).findall('object')) == count
            assert z.read(image_name) == image_bytes()
            assert ('/train/images/' in image_name) == (count > 0)
        contents_name = next(n for n in names if n.endswith('/contents.txt'))
        stored = json.loads(z.read(contents_name))
        selected_refs = {(ids[t], d) for t, d in selected}
        for row in stored[1][2:]:
            assert row['selected'] == ((row['tile'], row['id_in_tile']) in selected_refs)
    if selected == [(0, 0)]:
        # Exercise the real current ZIP writer's layout through restore again.
        next_stage = staging.parent / 'next-stage'
        next_stage.mkdir()
        monkeypatch.setattr(towerscout, '_make_session_tmpdir', lambda: str(next_stage))
        response = client.post('/uploaddataset', data={'dataset': (io.BytesIO(payload), 'dataset.zip')})
        assert response.status_code == 200
        assert not staging.exists()
        with client.session_transaction() as state:
            assert all(Path(tile['filename']).is_file() for tile in state['detections'])
            assert [r['selected'] for r in json.loads(state['results'])[2:]] == [True, False, False]


def test_manual_only_export_deselects_ml_without_changing_manual_boundary(review, monkeypatch):
    client, _, _ = review
    response = client.post('/uploaddataset', data={'dataset': (archive(dataset()), 'dataset.zip')})
    assert response.status_code == 200
    def offline_geocoder(**kwargs):
        raise RuntimeError('synthetic offline fixture')
    monkeypatch.setattr(towerscout, 'create_geocoding_service', offline_geocoder)
    manual = dict(tile=7, centerx=.5, centery=.5, w=.2, h=.2, inside=False)
    response = client.post('/getdataset', data={'include': '[]', 'additions': json.dumps([manual])})
    assert response.status_code == 200
    payload = response.get_data()
    response.close()
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        labels = {Path(n).name: z.read(n).decode().splitlines() for n in z.namelist() if n.endswith(('/tile0.txt', '/tile1.txt'))}
        assert labels == {'tile0.txt': ['0 0.5 0.5 0.2 0.2'], 'tile1.txt': []}
        stored = json.loads(z.read(next(n for n in z.namelist() if n.endswith('/contents.txt'))))
        assert all(not row['selected'] for row in stored[1][2:4])
        assert stored[1][-1]['selected'] is True and stored[1][-1]['inside'] is False


def test_explicit_legacy_contents_selection_remains_supported(tmp_path):
    data = dataset()
    with towerscout.app.test_request_context():
        towerscout.session['results'] = json.dumps(data[1])
        towerscout.write_contents_file(str(tmp_path), copy.deepcopy(data[0]), None, {1}, [], False)
    stored = json.loads((tmp_path / 'contents.txt').read_text())
    assert [row['selected'] for row in stored[1][2:]] == [False, True]


@pytest.mark.parametrize('extension,format', [('jpg', 'JPEG'), ('jpeg', 'JPEG'),
    ('png', 'PNG'), ('tif', 'TIFF'), ('tiff', 'TIFF'), ('jpg', 'PNG'), ('jpg', 'TIFF')])
def test_accepted_image_formats_remain_images_in_export(review, extension, format):
    client, _, _ = review
    data = dataset()
    data[0][0]['filename'] = f'old/tile0.{extension}'
    image = image_bytes(format)
    entries = {f'old/train/images/tile0.{extension}': image,
               'old/train/images/tile1.jpg': image_bytes()}
    response = client.post('/uploaddataset', data={'dataset': (archive(data, entries), 'dataset.zip')})
    assert response.status_code == 200
    response = client.post('/getdataset', data={'include': '[{"tile":7,"detection":0}]', 'additions': '[]'})
    assert response.status_code == 200
    payload = response.get_data()
    response.close()
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        name = next(n for n in z.namelist() if n.endswith(f'/tile0.{extension}'))
        assert '/train/images/' in name
        assert z.read(name) == image


@pytest.mark.parametrize('index', [-1, True, 1.0, 999])
def test_invalid_detection_index_does_not_select_other_annotations(review, index):
    client, _, _ = review
    assert client.post('/uploaddataset', data={'dataset': (archive(dataset()), 'dataset.zip')}).status_code == 200
    response = client.post('/getdataset', data={'include': json.dumps([{'tile':7, 'detection':index}]), 'additions': '[]'})
    assert response.status_code == 200
    payload = response.get_data()
    response.close()
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        for name in z.namelist():
            if name.endswith(('/tile0.txt', '/tile1.txt')):
                assert z.read(name) == b''
        stored = json.loads(z.read(next(n for n in z.namelist() if n.endswith('/contents.txt'))))
        assert all(not row['selected'] for row in stored[1][2:])


@pytest.mark.parametrize('limit', ['MAX_IMAGE_PIXELS', 'MAX_FILE_SIZE'])
def test_restore_applies_existing_image_budgets_before_commit(review, monkeypatch, limit):
    client, staging, previous = review
    # Allow the archive upload itself; the image validator still uses its
    # existing byte/pixel policy. Small synthetic limits avoid large fixtures.
    monkeypatch.setattr(towerscout.TowerScoutValidator, 'validate_dataset_file', lambda file: file)
    monkeypatch.setattr(towerscout.TowerScoutValidator, limit, 32)
    response = client.post('/uploaddataset', data={'dataset': (archive(dataset()), 'dataset.zip')})
    assert response.status_code == 400
    assert not staging.exists() and (previous / 'keep.jpg').exists()
    with client.session_transaction() as state:
        assert state['results'] == 'previous'
