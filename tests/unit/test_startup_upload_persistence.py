"""Fresh application processes must preserve the documented uploads volume."""
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('preexisting', [True, False])
def test_startup_preserves_uploads_across_fresh_processes(tmp_path, preexisting):
    runtime = tmp_path / 'runtime with spaces'
    uploads = runtime / 'uploads'
    expected = {'saved-image.png': b'preserved uploaded image',
                'nested/support.txt': b'preserved support attachment'}
    if preexisting:
        for relative, content in expected.items():
            path = uploads / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    env = os.environ.copy()
    paths = {
        'TOWERSCOUT_CONFIG_DIR': 'config', 'TOWERSCOUT_LOG_DIR': 'logs',
        'TOWERSCOUT_CACHE_DIR': 'cache', 'TOWERSCOUT_TEMP_DIR': 'temp',
        'TOWERSCOUT_FLASK_SESSION_DIR': 'sessions', 'UPLOAD_DIR': 'uploads',
        'YOLO_CONFIG_DIR': 'yolo', 'TORCH_HOME': 'torch', 'MODEL_PARAMS_DIR': 'models',
    }
    env.update({key: str(runtime / value) for key, value in paths.items()})
    env.update({'PYTHONPATH': str(ROOT / 'webapp'), 'TOWERSCOUT_DEVICE': 'cpu',
                'TOWERSCOUT_LAZY_MODEL_INIT': '1', 'TOWERSCOUT_STARTUP_PRELOAD': '0'})
    config = runtime / 'config'
    config.mkdir(parents=True)
    (config / '.env').write_text('FLASK_SECRET_KEY=startup-test-only\n')
    for _ in range(2):
        result = subprocess.run([sys.executable, '-c', 'import towerscout'],
                                cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)
        assert result.returncode == 0, result.stdout + result.stderr
        assert uploads.is_dir()
        for relative, content in expected.items():
            if preexisting:
                assert (uploads / relative).is_file(), f'Startup deleted {relative}'
                assert (uploads / relative).read_bytes() == content
