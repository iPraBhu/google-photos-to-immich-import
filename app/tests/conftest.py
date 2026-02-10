import pytest

@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("httpx.get", raising=False)
    monkeypatch.delattr("httpx.AsyncClient.get", raising=False)
    monkeypatch.delattr("httpx.AsyncClient.post", raising=False)
