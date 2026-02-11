import pytest

@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Prevent accidental HTTP requests during testing"""
    # Instead of deleting methods, we'll monkeypatch them to raise an error
    # This allows tests to properly mock them when needed
    def mock_http_method(*args, **kwargs):
        raise RuntimeError("HTTP request not mocked! Use monkeypatch to mock httpx methods in your test.")

    # Only patch if the methods exist
    if hasattr(httpx, 'get'):
        monkeypatch.setattr("httpx.get", mock_http_method)
    if hasattr(httpx.AsyncClient, 'get'):
        monkeypatch.setattr("httpx.AsyncClient.get", mock_http_method)
    if hasattr(httpx.AsyncClient, 'post'):
        monkeypatch.setattr("httpx.AsyncClient.post", mock_http_method)
