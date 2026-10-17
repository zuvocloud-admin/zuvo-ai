from typing import Optional, List
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.tenant import Tenant
from app.models.user import User
from app.models.whatsapp_number import WhatsAppNumber
from app.models.customer import Customer
from app.models.message import Message
from app.schemas.dashboard import (
    DashboardFeedResponse,
    DashboardMetrics,
    WorkerSummary,
    DashboardMessageItem
)
from app.core.logging import logger


class DashboardService:
    """
    Implements Owner Command Center and Gate G6 Multi-Worker / Customer 360° views.
    """

    @staticmethod
    async def get_dashboard_feed(
        db: AsyncSession,
        tenant_id: str,
        worker_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        customer_phone: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> DashboardFeedResponse:
        # 1. Fetch Tenant Profile
        tenant = await db.get(Tenant, tenant_id)
        business_name = tenant.business_name if tenant else "Unknown Business"

        # 2. Fetch Active Workers & Line Summaries
        stmt_workers = (
            select(User)
            .where(User.tenant_id == tenant_id, User.is_active == True)
            .options(selectinload(User.assigned_numbers))
        )
        res_workers = await db.execute(stmt_workers)
        workers_list = res_workers.scalars().all()

        worker_summaries: List[WorkerSummary] = []
        for w in workers_list:
            assigned_num = w.assigned_numbers[0] if w.assigned_numbers else None
            worker_summaries.append(
                WorkerSummary(
                    worker_id=w.id,
                    worker_name=w.full_name,
                    designation=w.designation,
                    phone_number=w.phone_number,
                    meta_phone_number_id=assigned_num.meta_phone_number_id if assigned_num else "N/A",
                    total_messages_today=0,  # Will be populated
                    active_conversations_count=0
                )
            )

        # 3. Build Dynamic Filtering Query (Gate G6)
        stmt_msg = (
            select(Message)
            .where(Message.tenant_id == tenant_id)
            .options(
                selectinload(Message.customer),
                selectinload(Message.whatsapp_number).selectinload(WhatsAppNumber.assigned_user)
            )
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )

        # Apply Gate G6 Filter 1: Worker Isolation
        if worker_id:
            stmt_msg = stmt_msg.join(Message.whatsapp_number).where(
                WhatsAppNumber.assigned_user_id == worker_id
            )

        # Apply Gate G6 Filter 2: Customer 360° Unified View
        if customer_id:
            stmt_msg = stmt_msg.where(Message.customer_id == customer_id)
        elif customer_phone:
            stmt_msg = stmt_msg.where(
                (Message.sender_phone == customer_phone) | (Message.recipient_phone == customer_phone)
            )

        res_msg = await db.execute(stmt_msg)
        messages = res_msg.scalars().all()

        message_items: List[DashboardMessageItem] = []
        for m in messages:
            wa_num = m.whatsapp_number
            worker = wa_num.assigned_user if wa_num else None
            cust = m.customer

            message_items.append(
                DashboardMessageItem(
                    id=m.id,
                    wamid=m.wamid,
                    direction=m.direction,
                    sender_phone=m.sender_phone,
                    recipient_phone=m.recipient_phone,
                    message_type=m.message_type,
                    content=m.raw_content,
                    parsed_intent=m.parsed_intent,
                    confidence_score=m.confidence_score,
                    worker_id=worker.id if worker else None,
                    worker_name=worker.full_name if worker else "Unassigned",
                    worker_phone=wa_num.display_phone_number if wa_num else None,
                    customer_id=cust.id if cust else None,
                    customer_name=cust.company_name if cust else "Unknown",
                    customer_phone=cust.primary_phone if cust else (m.sender_phone if m.direction == "INBOUND" else m.recipient_phone),
                    created_at=m.created_at
                )
            )

        # 4. Aggregate Metrics
        total_inbound = await db.scalar(
            select(func.count(Message.id)).where(Message.tenant_id == tenant_id, Message.direction == "INBOUND")
        ) or 0
        total_outbound = await db.scalar(
            select(func.count(Message.id)).where(Message.tenant_id == tenant_id, Message.direction == "OUTBOUND")
        ) or 0
        active_customers = await db.scalar(
            select(func.count(Customer.id)).where(Customer.tenant_id == tenant_id)
        ) or 0

        metrics = DashboardMetrics(
            tenant_id=tenant_id,
            business_name=business_name,
            total_messages_today=total_inbound + total_outbound,
            total_inbound=total_inbound,
            total_outbound=total_outbound,
            active_workers_count=len(workers_list),
            active_customers_count=active_customers,
            pending_approvals_count=0
        )

        filter_applied = {
            "worker_id": worker_id,
            "customer_id": customer_id,
            "customer_phone": customer_phone,
            "limit": limit,
            "offset": offset
        }

        return DashboardFeedResponse(
            metrics=metrics,
            workers=worker_summaries,
            messages=message_items,
            filter_applied=filter_applied
        )
