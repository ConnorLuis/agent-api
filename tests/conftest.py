from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def unique_thread():
    def _make(prefix: str) -> str:
        return f"{prefix}-{uuid4().hex[:8]}"

    return _make