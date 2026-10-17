import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class AuditLog(Base):
    """
    Immutable audit trail recording every critical action, AI decision, and tool invocation.
    """
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_type = Column(String(30), nullable=False)  # USER, AI_AGENT, SYSTEM, META_WEBHOOK
    actor_id = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False, index=True)  # INGEST_MESSAGE, DISPATCH_MESSAGE, APPROVE_ORDER
    entity_type = Column(String(50), nullable=True)  # message, conversation, order
    entity_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)  # JSON-encoded payload snapshot
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")
