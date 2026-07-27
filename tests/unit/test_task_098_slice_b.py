"""Task-098 Slice B Pillow and Waitress compatibility contracts."""

from __future__ import annotations

import http.client
import socket
import threading
from pathlib import Path

from waitress import wasyncore
from waitress.server import create_server

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_FILE = REPO_ROOT / "webapp" / "requirements.txt"
YOLO_RUNTIME_FILE = REPO_ROOT / "webapp" / "ts_yolov5.py"


def _request(
    port: int,
    method: str,
    path: str,
    body: bytes | None = None,
    *,
    read_body: bool = True,
):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request(method, path, body=body)
        response = connection.getresponse()
        return response.status, response.read() if read_body else b""
    finally:
        connection.close()


def test_slice_b_dependency_pins_are_consistent():
    requirements = REQUIREMENTS_FILE.read_text(encoding="utf-8").splitlines()
    yolo_runtime = YOLO_RUNTIME_FILE.read_text(encoding="utf-8")

    assert "Pillow==12.3.0" in requirements
    assert "waitress==3.0.2" in requirements
    assert "'pillow': {'min_version': '12.3.0'}" in yolo_runtime


def test_waitress_loopback_request_and_disconnect_contract():
    application_calls = []

    def application(environ, start_response):
        application_calls.append(environ["PATH_INFO"])
        start_response("200 OK", [("Content-Type", "application/json")])
        return [b'{"status":"ok"}']

    server = create_server(
        application,
        host="127.0.0.1",
        port=0,
        threads=1,
        max_request_body_size=1024,
        asyncore_loop_timeout=0.1,
    )
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    try:
        status, body = _request(server.effective_port, "GET", "/api/readiness")
        assert status == 200
        assert body == b'{"status":"ok"}'

        status, _ = _request(
            server.effective_port,
            "POST",
            "/upload",
            body=b"x" * 2048,
            read_body=False,
        )
        assert status == 413
        assert "/upload" not in application_calls

        with socket.create_connection(
            ("127.0.0.1", server.effective_port), timeout=5
        ) as malformed:
            malformed.sendall(
                b"GET /api/readiness HTTP/1.1\r\n"
                b"Host: 127.0.0.1\r\n"
                b"Malformed Header\r\n\r\n"
            )
            response = malformed.recv(1024)
        assert b"400 Bad Request" in response

        with socket.create_connection(
            ("127.0.0.1", server.effective_port), timeout=5
        ) as disconnected:
            disconnected.sendall(
                b"POST /upload HTTP/1.1\r\n"
                b"Host: 127.0.0.1\r\n"
                b"Content-Length: 10\r\n"
            )

        status, body = _request(server.effective_port, "GET", "/api/readiness")
        assert status == 200
        assert body == b'{"status":"ok"}'
    finally:
        server.task_dispatcher.shutdown()
        wasyncore.close_all(server._map)
        server_thread.join(timeout=5)

    assert not server_thread.is_alive()
