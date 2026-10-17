import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(150), nullable=True)
    primary_phone = Column(String(20), nullable=False, index=True)
    credit_limit = Column(Float, default=0.0)
    current_outstanding = Column(Float, default=0.0)
    payment_terms_days = Column(Integer, default=30)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("tenant_id", "primary_phone", name="uq_tenant_customer_phone"),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="customers")
    conversations = relationship("Conversation", back_populates="customer")
    messages = relationship("Message", back_populates="customer")
