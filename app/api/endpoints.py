from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.utils.immich_client import ImmichClient
from app.models.job import Job, JobStatus, AuthMode
from app.db.session import get_db
from app.utils.crypto import encrypt_secret
from sqlalchemy.orm import Session
from fastapi import Depends
from app.worker.worker import queue
import uuid

jobs_router = APIRouter()
immich_router = APIRouter()
health_router = APIRouter()

class TestLoginRequest(BaseModel):
    immich_url: str
    auth_mode: str
    api_key: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class CreateJobRequest(BaseModel):
    immich_url: str
    api_key: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    album_links: List[str]
    create_album: bool = True
    skip_duplicates: bool = True
    download_concurrency: int = 3
    upload_concurrency: int = 3
    store_staging: bool = False

@health_router.get("/")
def healthz():
    return {"status": "ok"}

@immich_router.post("/test-login")
async def test_login(req: TestLoginRequest):
    try:
        client = ImmichClient(req.immich_url)
        
        if req.auth_mode == "API_KEY":
            if not req.api_key:
                return {"ok": False, "message": "API key is required"}
            success, user_info = await client.test_api_key(req.api_key)
        else:  # CREDENTIALS
            if not req.email or not req.password:
                return {"ok": False, "message": "Email and password are required"}
            success, user_info = await client.test_login(req.email, req.password)
        
        if success:
            return {
                "ok": True, 
                "message": f"✅ Connected successfully as {user_info.get('email', 'user')}!",
                "user": user_info
            }
        else:
            return {"ok": False, "message": "❌ Login failed. Check your credentials and server URL."}
    except Exception as e:
        return {"ok": False, "message": f"❌ Error: {str(e)}"}

@jobs_router.post("/")
async def create_job(req: CreateJobRequest, db: Session = Depends(get_db)):
    try:
        # Determine auth mode
        auth_mode = AuthMode.API_KEY if req.api_key else AuthMode.CREDENTIALS
        
        # Build options dict
        options = {
            "create_album": req.create_album,
            "skip_duplicates": req.skip_duplicates,
            "download_concurrency": req.download_concurrency,
            "upload_concurrency": req.upload_concurrency,
            "store_staging": req.store_staging
        }
        
        # Encrypt credentials
        encrypted_api_key = encrypt_secret(req.api_key) if req.api_key else None
        encrypted_email = encrypt_secret(req.email) if req.email else None
        encrypted_password = encrypt_secret(req.password) if req.password else None
        
        job = Job(
            id=uuid.uuid4(),
            immich_url=req.immich_url,
            immich_auth_mode=auth_mode,
            encrypted_api_key=encrypted_api_key,
            encrypted_email=encrypted_email,
            encrypted_password=encrypted_password,
            options=options,
            status=JobStatus.QUEUED
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Enqueue the job for processing
        queue.enqueue('app.worker.worker.import_job', str(job.id))
        
        return {
            "id": str(job.id),
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "immich_url": job.immich_url,
            "progress": job.progress
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@jobs_router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": str(job.id),
        "status": job.status.value,
        "created_at": job.created_at.isoformat(),
        "progress": job.progress,
        "last_error": job.last_error
    }

@jobs_router.get("/")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(20).all()
    return [{
        "id": str(job.id),
        "status": job.status.value,
        "created_at": job.created_at.isoformat(),
        "progress": job.progress
    } for job in jobs]

@jobs_router.post("/{job_id}/start")
def start_job(job_id: str):
    return JSONResponse({"message": "Job queued for processing"}, status_code=200)

@jobs_router.post("/{job_id}/cancel")
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.cancel_requested = True
    db.commit()
    return {"message": "Cancel requested"}

@jobs_router.post("/{job_id}/retry-failed")
def retry_failed(job_id: str):
    return JSONResponse({"message": "Retry not implemented"}, status_code=501)

@jobs_router.get("/{job_id}/events")
def job_events(job_id: str):
    return JSONResponse({"events": []}, status_code=200)
