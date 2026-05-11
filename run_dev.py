from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
PYTHON_EXE = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
WEB_DIR = ROOT_DIR / "apps" / "web"
NPM_CMD = "npm.cmd"
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_HOST = "127.0.0.1"
FRONTEND_PORT = 5173
STARTUP_TIMEOUT_SECONDS = 20


def start_process(command: list[str], cwd: Path, name: str) -> subprocess.Popen[str]:
    print(f"[start] {name}: {' '.join(command)}")
    return subprocess.Popen(
        command,
        cwd=str(cwd),
        env=os.environ.copy(),
        text=True,
    )


def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def find_pid_by_port(port: int) -> int | None:
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
        )
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                pid = int(parts[-1])
                return pid
    except Exception:
        pass
    return None


def kill_process_by_port(host: str, port: int, name: str) -> bool:
    pid = find_pid_by_port(port)
    if pid is None:
        print(f"[warn] {name} port {port} is in use but could not find PID")
        return False

    print(f"[kill] {name} port {port} is occupied by PID {pid}, killing...")
    try:
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, text=True)
        time.sleep(1)
        if not is_port_in_use(host, port):
            print(f"[kill] {name} port {port} freed successfully")
            return True
        else:
            print(f"[error] {name} port {port} still in use after kill attempt")
            return False
    except Exception as e:
        print(f"[error] failed to kill PID {pid}: {e}")
        return False


def ensure_port_free(host: str, port: int, name: str) -> bool:
    if not is_port_in_use(host, port):
        return True
    return kill_process_by_port(host, port, name)


def wait_for_port(host: str, port: int, proc: subprocess.Popen[str], name: str, timeout_seconds: int) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if proc.poll() is not None:
            print(f"[error] {name} exited early with code {proc.returncode}")
            return False
        if is_port_in_use(host, port):
            return True
        time.sleep(0.5)

    print(f"[error] {name} did not become ready within {timeout_seconds} seconds")
    return False


def wait_for_shutdown(processes: list[tuple[str, subprocess.Popen[str]]]) -> int:
    try:
        while True:
            for name, proc in processes:
                exit_code = proc.poll()
                if exit_code is not None:
                    print(f"[stop] {name} exited with code {exit_code}")
                    return exit_code
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[stop] received Ctrl+C")
        return 130


def terminate_process(proc: subprocess.Popen[str], name: str) -> None:
    if proc.poll() is not None:
        return

    print(f"[stop] terminating {name}...")
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        print(f"[stop] killing {name}...")
        proc.kill()


def main() -> int:
    if not PYTHON_EXE.exists():
        print(f"[error] Python interpreter not found: {PYTHON_EXE}")
        return 1

    if not WEB_DIR.exists():
        print(f"[error] Frontend directory not found: {WEB_DIR}")
        return 1

    if shutil.which(NPM_CMD) is None:
        print(f"[error] {NPM_CMD} not found in PATH")
        return 1

    if not ensure_port_free(BACKEND_HOST, BACKEND_PORT, "backend"):
        return 1

    if not ensure_port_free(FRONTEND_HOST, FRONTEND_PORT, "frontend"):
        return 1

    backend_cmd = [
        str(PYTHON_EXE),
        "-m",
        "uvicorn",
        "apps.api.app.main:app",
        "--host",
        BACKEND_HOST,
        "--port",
        str(BACKEND_PORT),
    ]
    frontend_cmd = [NPM_CMD, "run", "dev", "--", "--host", FRONTEND_HOST, "--port", str(FRONTEND_PORT)]

    backend = start_process(backend_cmd, ROOT_DIR, "backend")
    frontend: subprocess.Popen[str] | None = None
    try:
        if not wait_for_port(BACKEND_HOST, BACKEND_PORT, backend, "backend", STARTUP_TIMEOUT_SECONDS):
            return backend.returncode or 1

        print(f"[ready] backend: http://{BACKEND_HOST}:{BACKEND_PORT}/docs")

        frontend = start_process(frontend_cmd, WEB_DIR, "frontend")
        if not wait_for_port(FRONTEND_HOST, FRONTEND_PORT, frontend, "frontend", STARTUP_TIMEOUT_SECONDS):
            return frontend.returncode or 1

        print(f"[ready] frontend: http://{FRONTEND_HOST}:{FRONTEND_PORT}")
        print("[info] Press Ctrl+C to stop both services")
        return wait_for_shutdown([("backend", backend), ("frontend", frontend)])
    finally:
        if frontend is not None:
            terminate_process(frontend, "frontend")
        terminate_process(backend, "backend")


if __name__ == "__main__":
    raise SystemExit(main())
