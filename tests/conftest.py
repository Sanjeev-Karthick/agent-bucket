from collections.abc import Iterator
from pathlib import Path

import pytest
from agent_bucket.app import create_app
from agent_bucket.config import Settings
from fastapi.testclient import TestClient


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    demo = tmp_path / "demo"
    demo.mkdir()
    (demo / "keys.md").write_text(
        "Rotate access keys by creating a new credential, then revoke the old key."
    )
    (demo / "deploy.txt").write_text(
        "Deploy one container with SQLite WAL and a persistent local volume."
    )
    return Settings(
        _env_file=None,
        data_dir=tmp_path / "state",
        demo_dir=demo,
        ui_dir=tmp_path / "no-ui",
        embedding_provider="hash",
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as instance:
        instance.headers["Authorization"] = "Bearer " + settings.api_token.get_secret_value()
        yield instance
