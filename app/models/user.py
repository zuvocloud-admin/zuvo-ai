import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    phone_number = Column(String(20), nullable=False)
    role = Column(String(30), default="WORKER")  # OWNER, MANAGER, WORKER
    designation = Column(String(100), nullable=True)  # e.g., Counter Sales, Field Sales, Godown Dispatch
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    assigned_numbers = relationship("WhatsAppNumber", back_populates="assigned_user")
