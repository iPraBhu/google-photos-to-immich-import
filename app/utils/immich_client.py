import httpx
from typing import Optional, Dict, Any

class ImmichClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.access_token = access_token
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        elif self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        self.client = httpx.AsyncClient(headers=headers)

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
            temp_client = httpx.AsyncClient(headers={"x-api-key": api_key})
            url = f"{self.base_url}/api/users/me"
            resp = await temp_client.get(url)
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
        finally:
            await temp_client.aclose()

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
        try:
            # First, try to find existing album
            url = f"{self.base_url}/api/albums"
            resp = await self.client.get(url)
            if resp.status_code == 200:
                albums = resp.json()
                for album in albums:
                    if album.get("albumName") == title:
                        return album["id"]
            
            # If not found, create new album
            create_url = f"{self.base_url}/api/albums"
            resp = await self.client.post(create_url, json={"albumName": title})
            if resp.status_code == 201:
                return resp.json()["id"]
            else:
                raise Exception(f"Failed to create album: {resp.text}")
        except Exception as e:
            raise Exception(f"Album operation failed: {str(e)}")

    async def upload_asset(self, file_path: str, filename: str = None) -> Optional[str]:
        try:
            with open(file_path, "rb") as f:
                files = {"assetData": (filename or file_path.split("/")[-1], f, "application/octet-stream")}
                url = f"{self.base_url}/api/assets"
                resp = await self.client.post(url, files=files)
                if resp.status_code == 201:
                    data = resp.json()
                    return data["id"]
                else:
                    raise Exception(f"Upload failed: {resp.status_code} {resp.text}")
        except Exception as e:
            raise Exception(f"Asset upload failed: {str(e)}")

    async def add_asset_to_album(self, asset_id: str, album_id: str) -> bool:
        try:
            url = f"{self.base_url}/api/albums/{album_id}/assets"
            resp = await self.client.put(url, json={"ids": [asset_id]})
            return resp.status_code == 200
        except Exception as e:
            raise Exception(f"Failed to add asset to album: {str(e)}")
