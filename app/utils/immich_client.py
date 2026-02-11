import httpx
from typing import Optional

class ImmichClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.access_token = access_token
        self.client = httpx.AsyncClient()

    async def test_login(self, email: str, password: str) -> tuple[bool, Optional[dict]]:
        """Test login with email/password, return (success, user_info)"""
        try:
            url = f"{self.base_url}/api/auth/login"
            resp = await self.client.post(url, json={"email": email, "password": password})
            if resp.status_code == 201:
                data = resp.json()
                user_info = {
                    "email": data.get("userEmail"),
                    "name": data.get("name"),
                    "id": data.get("userId")
                }
                return True, user_info
            elif resp.status_code == 401:
                return False, None  # Invalid credentials
            else:
                raise Exception(f"HTTP {resp.status_code}: {resp.text}")
        except httpx.ConnectError:
            raise Exception("Cannot connect to Immich server. Please check the URL and ensure the server is running.")
        except httpx.TimeoutException:
            raise Exception("Connection to Immich server timed out. Please check your network connection.")
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")

    async def test_api_key(self, api_key: str) -> tuple[bool, Optional[dict]]:
        """Test API key, return (success, user_info)"""
        try:
            url = f"{self.base_url}/api/users/me"
            headers = {"x-api-key": api_key}
            resp = await self.client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                user_info = {
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "id": data.get("id")
                }
                return True, user_info
            elif resp.status_code == 401:
                return False, None  # Invalid API key
            else:
                raise Exception(f"HTTP {resp.status_code}: {resp.text}")
        except httpx.ConnectError:
            raise Exception("Cannot connect to Immich server. Please check the URL and ensure the server is running.")
        except httpx.TimeoutException:
            raise Exception("Connection to Immich server timed out. Please check your network connection.")
        except Exception as e:
            raise Exception(f"API key test failed: {str(e)}")

    async def get_token(self, email: str, password: str) -> Optional[str]:
        try:
            url = f"{self.base_url}/api/auth/login"
            resp = await self.client.post(url, json={"email": email, "password": password})
            if resp.status_code == 201:
                return resp.json().get("accessToken")
            return None
        except httpx.ConnectError:
            raise Exception("Cannot connect to Immich server. Please check the URL and ensure the server is running.")
        except httpx.TimeoutException:
            raise Exception("Connection to Immich server timed out. Please check your network connection.")
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")

    async def find_or_create_album(self, title: str) -> Optional[str]:
        # TODO: Implement Immich album search/create
        pass

    async def upload_asset(self, file_path: str) -> Optional[str]:
        # TODO: Implement asset upload
        pass

    async def add_asset_to_album(self, asset_id: str, album_id: str) -> bool:
        # TODO: Implement add asset to album
        pass
