import os
import tempfile
import hashlib
from pathlib import Path
import logging
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import rq
from redis import Redis
from app.models.job import Job, JobStatus
from app.models.album import Album, AlbumStatus
from app.models.item import Item, ItemStatus
from app.db.session import get_db
from app.utils.crypto import decrypt_secret, encrypt_secret
from app.utils.immich_client import ImmichClient
from app.utils.google_photos_extractor import GooglePhotosExtractor
from app.utils.dedupe import sha256_stream
from app.utils.exif import extract_exif
from sqlalchemy.orm import Session
import httpx

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_conn = Redis.from_url(redis_url)

queue = rq.Queue("import-queue", connection=redis_conn)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_job(job_id: str):
    db: Session = next(get_db())
    log_messages = []
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return
        
        # Skip paused jobs
        if job.status == JobStatus.PAUSED:
            return
        
        def log(msg):
            logger.info(msg)
            log_messages.append(msg)
            job.log_tail = "\n".join(log_messages[-10:])  # Keep last 10 lines
            db.commit()
        
        # Update status to RUNNING
        job.status = JobStatus.RUNNING
        job.progress = json.dumps({"stage": "starting", "albums_processed": 0, "total_albums": len(job.album_links), "items_processed": 0, "total_items": 0})
        db.commit()
        log(f"Starting import job {job_id}")
        
        # Decrypt credentials
        api_key = decrypt_secret(job.encrypted_api_key) if job.encrypted_api_key else None
        email = decrypt_secret(job.encrypted_email) if job.encrypted_email else None
        password = decrypt_secret(job.encrypted_password) if job.encrypted_password else None
        
        # Authenticate
        client = ImmichClient(job.immich_url, api_key=api_key)
        if not api_key:
            token = client.get_token(email, password)
            if not token:
                raise Exception("Failed to authenticate with Immich")
            client = ImmichClient(job.immich_url, access_token=token)
            # Store token
            job.encrypted_access_token = encrypt_secret(token)
            db.commit()
        
        # Prepare staging directory
        staging_dir = None
        if job.options.get('store_staging'):
            staging_dir = Path("data/staging") / str(job.id)
            staging_dir.mkdir(parents=True, exist_ok=True)
        
        total_items = 0
        processed_items = 0
        
        # Process each album link
        for i, link in enumerate(job.album_links):
            if job.cancel_requested:
                log("Job cancelled")
                job.status = JobStatus.CANCELLED
                db.commit()
                return
            
            log(f"Processing album {i+1}/{len(job.album_links)}: {link}")
            album_data = GooglePhotosExtractor.extract_album(link)
            if not album_data:
                log(f"Failed to extract album from {link}")
                continue
            
            # Check if album already processed
            existing_album = db.query(Album).filter(Album.job_id == job.id, Album.source_url == link).first()
            if existing_album and existing_album.status == AlbumStatus.DONE:
                log(f"Album already processed: {album_data['title']}")
                continue
            
            # Create album in Immich
            immich_album_id = client.find_or_create_album(album_data['title'])
            
            # Save/update album to DB
            if existing_album:
                db_album = existing_album
                db_album.immich_album_id = immich_album_id
                db_album.status = AlbumStatus.PENDING
            else:
                db_album = Album(
                    job_id=job.id,
                    source_url=link,
                    source_title=album_data['title'],
                    immich_album_id=immich_album_id,
                    status=AlbumStatus.PENDING
                )
                db.add(db_album)
            db.commit()
            
            total_items += len(album_data['items'])
            job.progress = json.dumps({"stage": "processing_albums", "albums_processed": i, "total_albums": len(job.album_links), "items_processed": processed_items, "total_items": total_items})
            db.commit()
            
            # Process items
            for j, item_data in enumerate(album_data['items']):
                if job.cancel_requested:
                    log("Job cancelled")
                    job.status = JobStatus.CANCELLED
                    db.commit()
                    return
                
                media_url = item_data['media_url']
                filename = item_data.get('filename_hint', 'unknown')
                
                # Check if item already processed
                existing_item = db.query(Item).filter(Item.job_id == job.id, Item.source_media_url == media_url).first()
                if existing_item and existing_item.status == ItemStatus.DONE:
                    log(f"Item already processed: {filename}")
                    processed_items += 1
                    continue
                
                log(f"Processing item {j+1}/{len(album_data['items'])}: {filename}")
                
                # Download to temp or staging
                @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
                def download():
                    resp = httpx.get(media_url, timeout=60)
                    resp.raise_for_status()
                    return resp.content
                
                try:
                    content = download()
                except Exception as e:
                    log(f"Failed to download {media_url}: {e}")
                    continue
                
                if staging_dir:
                    file_path = staging_dir / filename
                    with open(file_path, 'wb') as f:
                        f.write(content)
                else:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(content)
                        file_path = Path(tmp.name)
                
                # Compute sha256
                with open(file_path, 'rb') as f:
                    sha256 = sha256_stream(f)
                
                # Extract EXIF
                exif_data = extract_exif(str(file_path))
                
                # Check dedupe
                skip = False
                if job.options.get('skip_duplicates'):
                    existing = db.query(Item).filter(Item.sha256 == sha256, Item.status == ItemStatus.DONE).first()
                    if existing:
                        log(f"Duplicate found, skipping: {filename}")
                        skip = True
                
                asset_id = None
                if not skip:
                    # Upload to Immich
                    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
                    def upload():
                        return client.upload_asset(str(file_path), filename)
                    
                    try:
                        asset_id = upload()
                        if asset_id and immich_album_id:
                            client.add_asset_to_album(asset_id, immich_album_id)
                    except Exception as e:
                        log(f"Failed to upload {filename}: {e}")
                
                # Save/update to DB
                if existing_item:
                    db_item = existing_item
                    db_item.sha256 = sha256
                    db_item.exif_json = json.dumps(exif_data) if exif_data else None
                    db_item.status = ItemStatus.DONE if asset_id else ItemStatus.FAILED
                    db_item.immich_asset_id = asset_id
                else:
                    db_item = Item(
                        job_id=job.id,
                        album_id=db_album.id,
                        source_media_url=media_url,
                        source_filename=filename,
                        sha256=sha256,
                        exif_json=json.dumps(exif_data) if exif_data else None,
                        status=ItemStatus.DONE if asset_id else ItemStatus.FAILED,
                        immich_asset_id=asset_id
                    )
                    db.add(db_item)
                db.commit()
                
                processed_items += 1
                job.progress = json.dumps({"stage": "processing_items", "albums_processed": i+1, "total_albums": len(job.album_links), "items_processed": processed_items, "total_items": total_items})
                db.commit()
                
                # Clean up if not staging
                if not staging_dir:
                    file_path.unlink()
            
            db_album.status = AlbumStatus.DONE
            db.commit()
            log(f"Completed album: {album_data['title']}")
        
        job.status = JobStatus.DONE
        job.progress = json.dumps({"stage": "completed", "albums_processed": len(job.album_links), "total_albums": len(job.album_links), "items_processed": processed_items, "total_items": total_items})
        db.commit()
        log("Import job completed successfully")
        
    except Exception as e:
        logger.error(f"Job failed: {e}")
        job.status = JobStatus.FAILED
        job.last_error = str(e)
        job.log_tail = "\n".join(log_messages[-10:])
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    # For local testing
    pass
