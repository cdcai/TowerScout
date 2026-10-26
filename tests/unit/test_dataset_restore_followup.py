"""Regression coverage for bounded legacy, archive and metadata restore."""
import copy
import io
import json
import struct
import zipfile

import pytest
from PIL import Image
import towerscout
from ts_dataset import DatasetFormatError, check_zip_directory, validate_contents
from test_dataset_restore_safety import archive, contents


def test_known_legacy_ids_normalized_without_mutating_input():
    data = contents()
    del data[1][0]['id']
    original = copy.deepcopy(data)
    normalized = validate_contents(data)
    assert normalized[1][0]['id'] == 0
    assert data == original


@pytest.mark.parametrize('ambiguous', ['index', 'order', 'mixed'])
def test_ambiguous_legacy_layout_rejected(ambiguous):
    data = contents()
    del data[1][0]['id']
    if ambiguous == 'index':
        data[0][0]['index'] = 3
        data[1][1]['tile'] = 3
    elif ambiguous == 'order':
        data[1].reverse()
    else:
        data[0].append(dict(data[0][0], index=1))
        data[1].insert(1, dict(data[1][0], id=1))
    with pytest.raises(DatasetFormatError):
        validate_contents(data)


@pytest.mark.parametrize('label', ['0  0.5 0.5 0.1 0.1', '0\t0.5\t0.5\t0.1\t0.1', '0 0.5 0.5 0.1 0.1\n'])
def test_labels_roundtrip_as_separate_yolo_and_xml_objects(tmp_path, label):
    data = contents()
    data[0][0]['detections'] = [label, label]
    tile = validate_contents(data)[0][0]
    tile.update(filename=str(tmp_path / 'tile.jpg'), labelfilename=str(tmp_path / 'tile.txt'))
    with Image.new('RGB', (640, 640), 'white') as image:
        image.save(tile['filename'])
    towerscout.write_labels(0, tile, {(0, 0), (0, 1)}, [])
    assert (tmp_path / 'tile.txt').read_text().splitlines() == ['0 0.5 0.5 0.1 0.1'] * 2
    assert (tmp_path / 'tile.xml').read_text().count('<object>') == 2


def test_zip64_locator_rejected_before_zipfile_allocation(tmp_path):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as z:
        for i in range(1001):
            z.writestr(str(i), b'')
    raw = stream.getvalue()
    end = len(raw) - 22
    count, size, offset = struct.unpack('<4s4H2IH', raw[end:])[4:7]
    record = struct.pack('<4sQ2H2I4Q', b'PK\x06\x06', 44, 45, 45, 0, 0, count, count, size, offset)
    locator = struct.pack('<4sIQI', b'PK\x06\x07', 0, end, 1)
    normal_end = struct.pack('<4s4H2IH', b'PK\x05\x06', 0, 0, 0, 0, 0, end + 76, 0)
    target = tmp_path / 'zip64.zip'
    target.write_bytes(raw[:end] + record + locator + normal_end)
    with pytest.raises(DatasetFormatError, match='ZIP'):
        check_zip_directory(target, 1000)


def test_normal_zip_comment_supported(tmp_path):
    target = tmp_path / 'normal.zip'
    with zipfile.ZipFile(target, 'w') as z:
        z.writestr('file', b'content')
        z.comment = b'Ordinary archive comment'
    check_zip_directory(target, 1000)


def test_restore_projects_schema_and_redacts_urls_before_response_and_reexport(tmp_path, monkeypatch):
    data = contents()
    for row in (data[0][0], data[1][0], data[1][1]):
        row['url'] = 'https://example.invalid/tile?key=SYNTHETIC-ONLY&zoom=18'
        row['unknown_field'] = 'UNRECOGNIZED-CONTENT'
    staging = tmp_path / 'restore'
    staging.mkdir()
    monkeypatch.setattr(towerscout, '_make_session_tmpdir', lambda: str(staging))
    monkeypatch.setattr(towerscout.rate_limiter, 'is_allowed', lambda *a, **k: True)
    client = towerscout.app.test_client()
    response = client.post('/uploaddataset', data={'dataset': (archive(data), 'dataset.zip')})
    assert response.status_code == 200
    assert 'SYNTHETIC-ONLY' not in response.get_data(as_text=True)
    assert 'unknown_field' not in response.get_data(as_text=True)
    with client.session_transaction() as state:
        restored = copy.deepcopy(state['detections'])
        stored_results = state['results']
    with towerscout.app.test_request_context():
        towerscout.session['results'] = stored_results
        towerscout.write_contents_file(str(staging), restored, {(0, 0)}, set(), [], False)
    assert 'SYNTHETIC-ONLY' not in (staging / 'contents.txt').read_text()
    assert 'unknown_field' not in (staging / 'contents.txt').read_text()
    assert not (staging / 'dataset.zip').exists()


def test_metadata_budget_rejects_before_extraction_preserving_current_review(tmp_path, monkeypatch):
    staging = tmp_path / 'restore'
    staging.mkdir()
    previous = tmp_path / 'previous'
    previous.mkdir()
    (previous / 'keep').write_text('keep')
    monkeypatch.setattr(towerscout, '_make_session_tmpdir', lambda: str(staging))
    monkeypatch.setattr(towerscout.rate_limiter, 'is_allowed', lambda *a, **k: True)
    monkeypatch.setattr(towerscout, 'MAX_DATASET_METADATA_BYTES', 256, raising=False)
    client = towerscout.app.test_client()
    with client.session_transaction() as state:
        state.update(tmpdirname=str(previous), results='previous', detections=['previous'])
    response = client.post('/uploaddataset', data={'dataset': (archive(contents()), 'dataset.zip')})
    assert response.status_code == 400
    assert 'metadata' in response.json['error'].lower()
    assert not staging.exists() and (previous / 'keep').exists()
    with client.session_transaction() as state:
        assert state['results'] == 'previous'
