from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class AlbumStatus(str, enum.Enum):
    PENDING = "PENDING"
    DONE = "DONE"
    FAILED = "FAILED"

class Album(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    source_url = Column(String, nullable=False)
    source_title = Column(String, nullable=True)
    immich_album_id = Column(String, nullable=True)
    status = Column(Enum(AlbumStatus), nullable=False, default=AlbumStatus.PENDING)
    error = Column(Text, nullable=True)
