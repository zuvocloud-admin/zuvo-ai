from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.whatsapp_number import WhatsAppNumber
from app.models.user import User
from app.models.tenant import Tenant
from app.core.logging import logger


class RouterService:
    """
    Service responsible for deterministic routing of incoming WhatsApp events
    based on Meta's phone_number_id.
    Follows Single Responsibility Principle (SRP).
    """

    @staticmethod
    async def resolve_routing(
        db: AsyncSession,
        meta_phone_number_id: str
    ) -> Optional[Tuple[Tenant, Optional[User], WhatsAppNumber]]:
        """
        Resolves (Tenant, Worker/User, WhatsAppNumber) from Meta's phone_number_id.
        """
        stmt = (
            select(WhatsAppNumber)
            .where(
                WhatsAppNumber.meta_phone_number_id == meta_phone_number_id,
                WhatsAppNumber.status == "ACTIVE"
            )
            .options(
                selectinload(WhatsAppNumber.tenant),
                selectinload(WhatsAppNumber.assigned_user)
            )
        )
        
        result = await db.execute(stmt)
        wa_number = result.scalar_one_or_none()

        if not wa_number:
            logger.warning(f"Unregistered or inactive phone_number_id received: {meta_phone_number_id}")
            return None

        tenant = wa_number.tenant
        worker = wa_number.assigned_user

        logger.info(
            f"Resolved routing: phone_number_id={meta_phone_number_id} -> "
            f"Tenant='{tenant.business_name}' (ID: {tenant.id}), "
            f"Worker='{worker.full_name if worker else 'Unassigned'}' (ID: {worker.id if worker else 'None'})"
        )
        
        return tenant, worker, wa_number
