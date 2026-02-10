import pytest
from app.utils.immich_client import ImmichClient
import httpx

@pytest.mark.asyncio
async def test_test_login(monkeypatch):
    async def dummy_post(url, json):
        class DummyResp:
            status_code = 201
            async def json(self): return {"accessToken": "tok"}
        return DummyResp()
    client = ImmichClient("http://immich")
    monkeypatch.setattr(client.client, "post", dummy_post)
    assert await client.test_login("a@b.com", "pw")
