from fastapi import APIRouter
from app.api import endpoints

router = APIRouter()

router.include_router(endpoints.jobs_router, prefix="/api/jobs", tags=["jobs"])
router.include_router(endpoints.immich_router, prefix="/api/immich", tags=["immich"])
router.include_router(endpoints.health_router, prefix="/healthz", tags=["health"])
