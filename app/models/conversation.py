import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Conversation(Base):
    """
    Represents an ongoing communication thread between a Customer and a Worker's WhatsApp Line.
    """
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    whatsapp_number_id = Column(String(36), ForeignKey("whatsapp_numbers.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_phone = Column(String(20), nullable=False, index=True)
    status = Column(String(30), default="OPEN")  # OPEN, HELD_APPROVAL, RESOLVED, ARCHIVED
    last_message_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("whatsapp_number_id", "customer_phone", name="uq_number_customer_thread"),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="conversations")
    whatsapp_number = relationship("WhatsAppNumber", back_populates="conversations")
    customer = relationship("Customer", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
