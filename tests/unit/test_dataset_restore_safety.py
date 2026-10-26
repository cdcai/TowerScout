"""Exercise hostile restore inputs through the supported HTTP endpoint."""
import copy
import io
import json
import zipfile
from unittest.mock import Mock

import pytest
import towerscout
from PIL import Image


def contents():
    return [[{'index': 0, 'filename': 'old/tile.jpg', 'detections': ['0 0.5 0.5 0.1 0.1\n']}], [
        {'class': 1, 'class_name': 'tile', 'id': 0, 'x1': 1, 'x2': 2, 'y1': 2, 'y2': 1,
         'conf': 1, 'metadata': '<img src=x onerror="synthetic()">'},
        {'class': 0, 'class_name': 'tower', 'tile': 0, 'id_in_tile': 0, 'x1': 1.4, 'x2': 1.5,
         'y1': 1.5, 'y2': 1.4, 'conf': 0.8, 'secondary': 0.9, 'selected': True,
         'inside': False, 'address': '=1+1'},
    ], False]


def archive(data):
    stream = io.BytesIO()
    image_stream = io.BytesIO()
    with Image.new('RGB', (8, 8), 'white') as image:
        image.save(image_stream, format='JPEG')
    with zipfile.ZipFile(stream, 'w') as z:
        z.writestr('old/train/images/tile.jpg', image_stream.getvalue())
        z.writestr('contents.txt', json.dumps(data))
    stream.seek(0)
    return stream


@pytest.mark.parametrize('field,bad', [('selected', '=1+1'), ('inside', '=2+2'),
    ('conf', '0.9'), ('secondary', float('nan')), ('address', {'html': 'bad'}),
    ('x1', []), ('tile', 999), ('id_in_tile', 100), ('class_name', None)])
def test_hostile_fields_rejected_without_changing_review(tmp_path, monkeypatch, field, bad):
    data = contents()
    data[1][1][field] = bad
    staging = tmp_path / 'new'
    staging.mkdir()
    previous = tmp_path / 'old'
    previous.mkdir()
    (previous / 'keep').write_text('keep')
    monkeypatch.setattr(towerscout, '_make_session_tmpdir', lambda: str(staging))
    monkeypatch.setattr(towerscout.rate_limiter, 'is_allowed', lambda *a, **k: True)
    client = towerscout.app.test_client()
    with client.session_transaction() as state:
        state.update(tmpdirname=str(previous), results='previous', detections=['previous'])
    response = client.post('/uploaddataset', data={'dataset': (archive(data), 'dataset.zip')})
    assert response.status_code == 400
    assert not staging.exists() and (previous / 'keep').read_text() == 'keep'
    with client.session_transaction() as state:
        assert state['results'] == 'previous' and state['detections'] == ['previous']


def test_valid_full_tile_roundtrip_retains_outside_annotation(tmp_path, monkeypatch):
    data = contents()
    staging = tmp_path / 'restored'
    staging.mkdir()
    monkeypatch.setattr(towerscout, '_make_session_tmpdir', lambda: str(staging))
    monkeypatch.setattr(towerscout.rate_limiter, 'is_allowed', lambda *a, **k: True)
    client = towerscout.app.test_client()
    response = client.post('/uploaddataset', data={'dataset': (archive(data), 'dataset.zip')})
    assert response.status_code == 200
    assert response.json == data[1]
    with client.session_transaction() as state:
        restored = copy.deepcopy(state['detections'])
    with towerscout.app.test_request_context():
        towerscout.session['results'] = json.dumps(data[1])
        towerscout.write_contents_file(str(staging), restored, {(0, 0)}, set(), [], False)
    restored_data = json.loads((staging / 'contents.txt').read_text())
    towerscout.validate_contents(restored_data)
    assert restored_data[1][1]['selected'] is True
    assert restored_data[1][1]['inside'] is False


def test_query_and_path_secret_not_logged(monkeypatch):
    log = Mock()
    monkeypatch.setattr(towerscout.api_logger, 'warning', log)
    response = towerscout.app.test_client().get('/missing-SYNTHETIC-PATH?key=SYNTHETIC-QUERY')
    assert response.status_code == 404
    assert 'SYNTHETIC' not in str(log.call_args_list)


def test_directory_budget_applies_before_zipfile_allocation(tmp_path, monkeypatch):
    from ts_dataset import check_zip_directory, DatasetFormatError
    target = tmp_path / 'many.zip'
    with zipfile.ZipFile(target, 'w') as z:
        for i in range(1001):
            z.writestr(str(i), b'')
    with pytest.raises(DatasetFormatError):
        check_zip_directory(target, 1000)
    # A forged EOCD count must not bypass the actual bounded directory walk.
    payload = bytearray(target.read_bytes())
    payload[-14:-12] = b'\x01\x00'
    payload[-12:-10] = b'\x01\x00'
    target.write_bytes(payload)
    with pytest.raises(DatasetFormatError):
        check_zip_directory(target, 1000)


def test_same_site_get_cannot_cancel_and_navigation_keeps_exports(tmp_path):
    client = towerscout.app.test_client()
    with client.session_transaction() as state:
        state['tmpdirname'] = str(tmp_path)
    (tmp_path / 'keep').write_text('keep')
    assert client.get('/abort', headers={'Sec-Fetch-Site': 'same-site'}).status_code == 403
    assert client.get('/abort').status_code == 405
    assert client.get('/').status_code == 200
    assert (tmp_path / 'keep').read_text() == 'keep'
