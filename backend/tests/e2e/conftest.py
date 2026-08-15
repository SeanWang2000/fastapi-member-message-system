import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def frontend_server():
    frontend_dir = Path(__file__).resolve().parents[3] / "frontend"

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", "5173"],
        cwd=frontend_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(20):
        try:
            with socket.create_connection(("127.0.0.1", 5173), timeout=1):
                break
        except OSError:
            time.sleep(0.5)
    else:
        server.terminate()
        raise RuntimeError("Frontend server failed to start")

    yield

    server.terminate()
    server.wait()