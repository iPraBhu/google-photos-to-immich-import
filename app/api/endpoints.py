from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

jobs_router = APIRouter()
immich_router = APIRouter()
health_router = APIRouter()

@health_router.get("/")
def healthz():
    return {"status": "ok"}

# Placeholder endpoints for jobs and Immich auth
def not_implemented():
    return JSONResponse({"error": "Not implemented"}, status_code=status.HTTP_501_NOT_IMPLEMENTED)

@jobs_router.post("/")
def create_job():
    return not_implemented()

@jobs_router.get("/{job_id}")
def get_job(job_id: str):
    return not_implemented()

@jobs_router.post("/{job_id}/start")
def start_job(job_id: str):
    return not_implemented()

@jobs_router.post("/{job_id}/cancel")
def cancel_job(job_id: str):
    return not_implemented()

@jobs_router.post("/{job_id}/retry-failed")
def retry_failed(job_id: str):
    return not_implemented()

@jobs_router.get("/{job_id}/events")
def job_events(job_id: str):
    return not_implemented()

@immich_router.post("/test-login")
def test_login():
    return not_implemented()
