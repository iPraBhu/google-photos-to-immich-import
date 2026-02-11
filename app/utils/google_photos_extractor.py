import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import json

class GooglePhotosExtractor:
    @staticmethod
    def extract_album(link: str) -> Optional[dict]:
        # Best-effort HTML fetch and parse
        try:
            resp = httpx.get(link, timeout=30, follow_redirects=True)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Extract title from <title>
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else "Untitled Album"
            
            items = []
            
            # Try to find data in AF_initDataCallback scripts
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'AF_initDataCallback' in script.string:
                    # Extract the JSON data
                    match = re.search(r'AF_initDataCallback\((.*?)\);', script.string)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            # Parse the data structure (this may need adjustment based on actual structure)
                            # Typically, data[3][0] or similar contains album info
                            album_data = data[3] if len(data) > 3 else data
                            if isinstance(album_data, list) and len(album_data) > 0:
                                for item in album_data:
                                    if isinstance(item, list) and len(item) > 1:
                                        # Assume item[1] has media URL
                                        media_url = item[1] if isinstance(item[1], str) and 'photos.google.com' in item[1] else None
                                        if media_url:
                                            filename = media_url.split('/')[-1] if '/' in media_url else 'unknown'
                                            items.append({
                                                'media_url': media_url,
                                                'filename_hint': filename
                                            })
                        except json.JSONDecodeError:
                            pass
            
            # Fallback: look for img tags
            if not items:
                for img in soup.find_all('img'):
                    src = img.get('data-src') or img.get('src')
                    if src and ('photos.google.com' in src or 'lh3.googleusercontent.com' in src):
                        filename = src.split('/')[-1] if '/' in src else 'unknown'
                        items.append({
                            'media_url': src,
                            'filename_hint': filename
                        })
            
            return {
                "title": title,
                "items": items
            }
        except Exception as e:
            print(f"Error extracting album: {e}")
            return None
