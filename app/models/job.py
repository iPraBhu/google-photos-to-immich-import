import uuid
from sqlalchemy import Column, String, DateTime, Enum, JSON, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"

class AuthMode(str, enum.Enum):
    API_KEY = "API_KEY"
    CREDENTIALS = "CREDENTIALS"

class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.QUEUED)
    immich_url = Column(String, nullable=False)
    immich_auth_mode = Column(Enum(AuthMode), nullable=False)
    encrypted_api_key = Column(String, nullable=True)
    encrypted_email = Column(String, nullable=True)
    encrypted_password = Column(String, nullable=True)
    encrypted_access_token = Column(String, nullable=True)
    album_links = Column(JSON, nullable=False)
    options = Column(JSON, nullable=False)
    progress = Column(JSON, nullable=True)
    last_error = Column(Text, nullable=True)
    log_tail = Column(Text, nullable=True)
    cancel_requested = Column(Boolean, default=False)
