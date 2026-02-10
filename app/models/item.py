from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text, JSON, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
import enum

class ItemStatus(str, enum.Enum):
    PENDING = "PENDING"
    DOWNLOADING = "DOWNLOADING"
    UPLOADING = "UPLOADING"
    DONE = "DONE"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)
    source_media_url = Column(String, nullable=False)
    source_filename = Column(String, nullable=True)
    mime = Column(String, nullable=True)
    bytes = Column(Integer, nullable=True)
    sha256 = Column(String, nullable=True)
    exif_json = Column(JSON, nullable=True)
    metadata_quality = Column(String, nullable=True)
    status = Column(Enum(ItemStatus), nullable=False, default=ItemStatus.PENDING)
    immich_asset_id = Column(String, nullable=True)
    error = Column(Text, nullable=True)
