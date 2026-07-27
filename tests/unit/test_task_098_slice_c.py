"""Task-098 Slice C aiohttp provider-client compatibility contracts."""

from __future__ import annotations

import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import aiohttp
import pytest

import ts_maps
from ts_errors import NetworkError

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_FILE = REPO_ROOT / "webapp" / "requirements.txt"
TILE_BYTES = b"task-098-provider-tile"


class _ProviderTestServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        return


@pytest.fixture
def provider_server():
    state = {
        "retry_requests": 0,
        "slow_request_started": threading.Event(),
    }

    class ProviderHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, format_, *args):
            return

        def _write_response(self, status, body=b"", headers=None):
            self.send_response(status)
            for name, value in (headers or {}).items():
                self.send_header(name, value)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass

        def do_GET(self):
            if self.path.endswith("/redirect"):
                provider_path = self.path.removesuffix("/redirect")
                self._write_response(
                    302,
                    headers={"Location": f"{provider_path}/tile"},
                )
                return

            if self.path.endswith("/tile"):
                self._write_response(
                    200,
                    TILE_BYTES,
                    headers={
                        "Content-Type": "image/jpeg",
                        "X-Provider-Metadata": "imagery-v1",
                    },
                )
                return

            if self.path.endswith("/retry"):
                state["retry_requests"] += 1
                if state["retry_requests"] == 1:
                    self._write_response(429, headers={"Retry-After": "0"})
                else:
                    self._write_response(200, TILE_BYTES)
                return

            if self.path.endswith("/slow"):
                state["slow_request_started"].set()
                time.sleep(0.5)
                self._write_response(200, TILE_BYTES)
                return

            self._write_response(404)

    server = _ProviderTestServer(("127.0.0.1", 0), ProviderHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        yield base_url, state
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)

    assert not server_thread.is_alive()


def _run_fetch(url, directory, filename, *, max_retries=0):
    async def run():
        async with aiohttp.ClientSession() as session:
            await ts_maps.fetch(
                asyncio.Semaphore(1),
                session,
                url,
                str(directory),
                filename,
                0,
                max_retries=max_retries,
            )

    asyncio.run(run())


def test_slice_c_aiohttp_pin_is_exact():
    requirements = REQUIREMENTS_FILE.read_text(encoding="utf-8").splitlines()

    assert "aiohttp==3.14.2" in requirements


@pytest.mark.parametrize("provider", ["google", "azure"])
def test_provider_download_follows_redirect_and_writes_response(
    provider_server,
    monkeypatch,
    tmp_path,
    provider,
):
    base_url, _ = provider_server
    monkeypatch.setattr(ts_maps, "_provider_name_from_url", lambda url: provider)

    _run_fetch(
        f"{base_url}/{provider}/redirect",
        tmp_path,
        f"{provider}-tile-",
    )

    assert (tmp_path / f"{provider}-tile-0.jpg").read_bytes() == TILE_BYTES


def test_provider_retry_after_header_is_parsed_before_retry(
    provider_server,
    monkeypatch,
    tmp_path,
):
    base_url, state = provider_server
    monkeypatch.setattr(ts_maps, "_provider_name_from_url", lambda url: "google")

    _run_fetch(
        f"{base_url}/google/retry",
        tmp_path,
        "retry-tile-",
        max_retries=1,
    )

    assert state["retry_requests"] == 2
    assert (tmp_path / "retry-tile-0.jpg").read_bytes() == TILE_BYTES


def test_provider_timeout_is_categorized_without_retry(
    provider_server,
    monkeypatch,
    tmp_path,
):
    base_url, _ = provider_server
    real_client_timeout = aiohttp.ClientTimeout
    monkeypatch.setattr(
        ts_maps.aiohttp,
        "ClientTimeout",
        lambda total: real_client_timeout(total=0.02),
    )
    monkeypatch.setattr(ts_maps, "_provider_name_from_url", lambda url: "azure")

    with pytest.raises(NetworkError) as exc_info:
        _run_fetch(
            f"{base_url}/azure/slow",
            tmp_path,
            "timeout-tile-",
        )

    assert exc_info.value.details["provider"] == "azure"
    assert exc_info.value.details["category"] == ts_maps.PROVIDER_TIMEOUT
    assert exc_info.value.details["timeout"] == 30


def test_provider_download_cancellation_propagates(
    provider_server,
    monkeypatch,
    tmp_path,
):
    base_url, state = provider_server
    monkeypatch.setattr(ts_maps, "_provider_name_from_url", lambda url: "google")

    async def run():
        async with aiohttp.ClientSession() as session:
            task = asyncio.create_task(
                ts_maps.fetch(
                    asyncio.Semaphore(1),
                    session,
                    f"{base_url}/google/slow",
                    str(tmp_path),
                    "cancelled-tile-",
                    0,
                    max_retries=0,
                )
            )
            request_started = await asyncio.to_thread(
                state["slow_request_started"].wait,
                2,
            )
            assert request_started
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task

    asyncio.run(run())
    assert not (tmp_path / "cancelled-tile-0.jpg").exists()


def test_provider_client_error_payload_redacts_credentials(tmp_path):
    secret = "AIzaSyTask098SecretCredential123456789012"
    url = "https://maps.googleapis.com/maps/api/staticmap" f"?center=0,0&key={secret}"

    class FailingRequest:
        async def __aenter__(self):
            raise aiohttp.ClientConnectionError(f"connection failed for {url}")

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

    class FailingSession:
        def get(self, request_url, timeout):
            assert request_url == url
            assert timeout.total == 30
            return FailingRequest()

    async def run():
        await ts_maps.fetch(
            asyncio.Semaphore(1),
            FailingSession(),
            url,
            str(tmp_path),
            "failed-tile-",
            0,
            max_retries=0,
        )

    with pytest.raises(NetworkError) as exc_info:
        asyncio.run(run())

    payload = json.dumps(exc_info.value.to_dict())
    assert secret not in payload
    assert "REDACTED" in payload
    assert exc_info.value.details["provider"] == "google"
    assert exc_info.value.details["category"] == ts_maps.PROVIDER_NETWORK_BLOCKED
