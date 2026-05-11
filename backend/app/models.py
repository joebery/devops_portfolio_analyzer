from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base
import uuid
from datetime import datetime, timezone

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_url = Column(Text, nullable=False)
    owner = Column(String(255), nullable=False)
    repo_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)