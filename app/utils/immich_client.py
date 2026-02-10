import httpx
from typing import Optional

class ImmichClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.access_token = access_token
        self.client = httpx.AsyncClient()

    async def test_login(self, email: str, password: str) -> bool:
        url = f"{self.base_url}/api/auth/login"
        resp = await self.client.post(url, json={"email": email, "password": password})
        return resp.status_code == 201

    async def get_token(self, email: str, password: str) -> Optional[str]:
        url = f"{self.base_url}/api/auth/login"
        resp = await self.client.post(url, json={"email": email, "password": password})
        if resp.status_code == 201:
            return resp.json().get("accessToken")
        return None

    async def find_or_create_album(self, title: str) -> Optional[str]:
        # TODO: Implement Immich album search/create
        pass

    async def upload_asset(self, file_path: str) -> Optional[str]:
        # TODO: Implement asset upload
        pass

    async def add_asset_to_album(self, asset_id: str, album_id: str) -> bool:
        # TODO: Implement add asset to album
        pass
