import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Message(Base):
    """
    Stores persisted normalized inbound & outbound messages.
    Includes worker attribution, parsed intent, confidence score, and wamid.
    """
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    whatsapp_number_id = Column(String(36), ForeignKey("whatsapp_numbers.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    
    wamid = Column(String(120), unique=True, nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # INBOUND, OUTBOUND
    sender_phone = Column(String(20), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    message_type = Column(String(20), default="text")  # text, audio, image, document
    raw_content = Column(Text, nullable=False)
    
    parsed_intent = Column(String(50), nullable=True)  # CREATE_ORDER, INQUIRY_PRICE_STOCK, etc.
    confidence_score = Column(Float, nullable=True)
    status = Column(String(30), default="PROCESSED")  # RECEIVED, PROCESSED, NEEDS_REVIEW, FAILED
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")
    whatsapp_number = relationship("WhatsAppNumber", back_populates="messages")
    customer = relationship("Customer", back_populates="messages")
