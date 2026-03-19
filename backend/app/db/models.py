from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, JSON, UUID
import uuid
from datetime import datetime, timezone
import enum
from app.db.database import Base
from app.core.config import DEFAULT_USER_TOKEN_LIMIT

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    auth_provider = Column(String, default="local")
    token_limit = Column(Integer, default=DEFAULT_USER_TOKEN_LIMIT)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    last_reset_date = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SOPJob(Base):
    __tablename__ = "sop_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    current_step = Column(String, default="pending")
    input_data = Column(JSON, nullable=False)  # Stores FullUserInput
    result_report = Column(JSON, nullable=True)  # Stores SOPReport
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
