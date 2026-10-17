import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class WhatsAppNumber(Base):
    """
    Maps Meta Cloud API's phone_number_id to an internal Worker and Business Tenant.
    Enables single webhook multi-number routing.
    """
    __tablename__ = "whatsapp_numbers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    meta_phone_number_id = Column(String(50), nullable=False, unique=True, index=True)
    display_phone_number = Column(String(20), nullable=False)
    display_name = Column(String(100), nullable=True)
    status = Column(String(20), default="ACTIVE")  # ACTIVE, PAUSED, REVOKED
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="whatsapp_numbers")
    assigned_user = relationship("User", back_populates="assigned_numbers")
    conversations = relationship("Conversation", back_populates="whatsapp_number")
    messages = relationship("Message", back_populates="whatsapp_number")
