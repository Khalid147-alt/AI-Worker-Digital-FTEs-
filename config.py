from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv is optional for local runs
    def load_dotenv(*args, **kwargs):
        return False


REPO_ROOT = Path(__file__).resolve().parent
ENV_FILE = REPO_ROOT / ".env"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file(ENV_FILE)
load_dotenv(ENV_FILE, override=False)


def _resolve_env_path(name: str) -> Path:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Copy .env.example to .env and set the required path before starting the service."
        )

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def get_runtime_paths() -> tuple[Path, Path]:
    vault_path = _resolve_env_path("VAULT_PATH")
    scripts_dir = _resolve_env_path("SCRIPTS_DIR")

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault path does not exist: {vault_path}")
    if not scripts_dir.exists():
        raise FileNotFoundError(f"Scripts directory does not exist: {scripts_dir}")

    return vault_path, scripts_dir


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Copy .env.example to .env and set the required variable before starting the service."
        )
    return value
