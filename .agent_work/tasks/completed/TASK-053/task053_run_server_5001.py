import os
import sys

from waitress import serve


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WEBAPP_DIR = os.path.join(REPO_ROOT, "webapp")
PROXY_ENV_VARS = (
    "ALL_PROXY",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "all_proxy",
    "http_proxy",
    "https_proxy",
)


def clear_proxy_environment():
    # The isolated helper server must use the host network directly so
    # reverse-geocoding requests are not routed through the tool wrapper's
    # placeholder proxy values.
    for key in PROXY_ENV_VARS:
        os.environ.pop(key, None)


def ensure_utf8_stdio():
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def main():
    os.chdir(WEBAPP_DIR)
    if WEBAPP_DIR not in sys.path:
        sys.path.insert(0, WEBAPP_DIR)
    clear_proxy_environment()
    ensure_utf8_stdio()

    import towerscout

    towerscout.get_custom_models()
    towerscout.engine_default = sorted(
        towerscout.engines.items(),
        key=lambda item: -item[1]["ts"]
    )[0][0]
    towerscout.dev = 1

    serve(towerscout.app, host="0.0.0.0", port=5001)


if __name__ == "__main__":
    main()
