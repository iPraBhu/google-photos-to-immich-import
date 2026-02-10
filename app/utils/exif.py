import subprocess
import json
from typing import Optional

def extract_exif(file_path: str) -> Optional[dict]:
    try:
        result = subprocess.run([
            "exiftool", "-j", "-n", file_path
        ], capture_output=True, check=True, text=True)
        exif_list = json.loads(result.stdout)
        return exif_list[0] if exif_list else None
    except Exception as e:
        return None
