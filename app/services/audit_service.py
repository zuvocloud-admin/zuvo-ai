import json
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.core.logging import logger


class AuditService:
    """
    Records immutable audit log records for security, tracing, and governance.
    """

    @staticmethod
    async def log_event(
        db: AsyncSession,
        tenant_id: str,
        actor_type: str,
        action: str,
        actor_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[Any] = None
    ) -> AuditLog:
        details_str = json.dumps(details) if isinstance(details, (dict, list)) else (str(details) if details else None)
        
        audit_entry = AuditLog(
            tenant_id=tenant_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details_str
        )
        
        db.add(audit_entry)
        await db.flush()
        logger.debug(f"[AUDIT] Tenant={tenant_id} Action={action} Entity={entity_type}:{entity_id}")
        return audit_entry
