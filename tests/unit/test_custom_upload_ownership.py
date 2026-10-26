import io
from unittest.mock import Mock

from PIL import Image
import pytest
import towerscout


def image_bytes():
    result = io.BytesIO()
    Image.new('RGB', (16, 16)).save(result, format='JPEG')
    result.seek(0)
    return result


def test_upload_replacement_is_session_owned_and_survives_reload(tmp_path, monkeypatch):
    monkeypatch.setattr(towerscout, 'UPLOAD_DIR', tmp_path)
    monkeypatch.setattr(towerscout, 'get_engine', lambda _: Mock(detect=Mock(return_value=[[]])))
    monkeypatch.setattr(towerscout.rate_limiter, 'is_allowed', lambda *a, **k: True)
    monkeypatch.setattr(towerscout.TowerScoutValidator, 'validate_engine', lambda _: 'synthetic')
    clients = [towerscout.app.test_client(), towerscout.app.test_client()]
    def upload(client):
        r = client.post('/getobjectscustom', data={'engine': 'synthetic', 'image': (image_bytes(), 'same.jpg')})
        assert r.status_code == 200
        return r.headers['X-TowerScout-Upload-URL']
    first, other = [upload(c) for c in clients]
    assert first != other
    assert clients[0].get(other).status_code == 404
    assert clients[0].get(first).status_code == 200
    clients[0].get('/')
    assert clients[0].get(first).status_code == 200
    replacement = upload(clients[0])
    assert clients[0].get(first).status_code == 404
    assert clients[0].get(replacement).status_code == 200
    assert clients[1].get(other).status_code == 200
    assert len(list(tmp_path.iterdir())) == 2


def test_collision_does_not_delete_existing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(towerscout, 'UPLOAD_DIR', tmp_path)
    monkeypatch.setattr(towerscout, 'get_engine', lambda _: Mock())
    monkeypatch.setattr(towerscout.secrets, 'token_hex', lambda _: 'a' * 32)
    existing = tmp_path / ('a' * 32 + '.jpg')
    existing.write_bytes(b'keep')
    file = Mock(filename='same.jpg')
    with towerscout.app.test_request_context():
        with pytest.raises(FileExistsError):
            towerscout._run_custom_image_detection(0, 'synthetic', file)
    assert existing.read_bytes() == b'keep'
    file.save.assert_not_called()
