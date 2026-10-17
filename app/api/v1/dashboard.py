from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.whatsapp_number import WhatsAppNumber
from app.schemas.dashboard import DashboardFeedResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Owner Dashboard & Gate G6"])


@router.get("/feed", response_model=DashboardFeedResponse, summary="Owner Command Center Live Feed (Gate G6)")
async def get_dashboard_feed(
    tenant_id: str = Query(..., description="Target business tenant UUID"),
    worker_id: Optional[str] = Query(None, description="Filter by assigned Worker ID (Worker-Level Isolation)"),
    customer_id: Optional[str] = Query(None, description="Filter by Customer ID (Customer 360° Unified View)"),
    customer_phone: Optional[str] = Query(None, description="Filter by Customer Phone Number"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the real-time aggregated message timeline for the business owner.
    Supports Gate G6:
      - Worker-Level Isolation: Owner inspects a specific employee's line.
      - Customer 360° View: Unifies all 5 worker lines into a single chronological timeline for a customer.
    """
    return await DashboardService.get_dashboard_feed(
        db=db,
        tenant_id=tenant_id,
        worker_id=worker_id,
        customer_id=customer_id,
        customer_phone=customer_phone,
        limit=limit,
        offset=offset
    )


@router.get("/customers", summary="List Tenant Customers & Credit Ledgers")
async def list_customers(
    tenant_id: str = Query(..., description="Target business tenant UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all registered wholesale customers for the tenant with their credit standing.
    """
    stmt = select(Customer).where(Customer.tenant_id == tenant_id).order_by(Customer.company_name)
    res = await db.execute(stmt)
    customers = res.scalars().all()
    return [
        {
            "id": c.id,
            "company_name": c.company_name,
            "contact_person": c.contact_person,
            "primary_phone": c.primary_phone,
            "credit_limit": c.credit_limit,
            "current_outstanding": c.current_outstanding,
            "is_blocked": c.is_blocked,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in customers
    ]


@router.get("/tenants", summary="List All Tenants & Connected Lines")
async def list_tenants(db: AsyncSession = Depends(get_db)):
    """
    Lists registered tenants, active workers, and connected WhatsApp lines.
    """
    stmt = (
        select(Tenant)
        .where(Tenant.is_active == True)
        .options(
            selectinload(Tenant.users),
            selectinload(Tenant.whatsapp_numbers).selectinload(WhatsAppNumber.assigned_user)
        )
    )
    res = await db.execute(stmt)
    tenants = res.scalars().all()

    output = []
    for t in tenants:
        lines = []
        for wn in t.whatsapp_numbers:
            lines.append({
                "number_id": wn.id,
                "meta_phone_number_id": wn.meta_phone_number_id,
                "display_phone_number": wn.display_phone_number,
                "assigned_worker": wn.assigned_user.full_name if wn.assigned_user else "Unassigned",
                "worker_id": wn.assigned_user.id if wn.assigned_user else None,
                "status": wn.status
            })
        
        output.append({
            "tenant_id": t.id,
            "business_name": t.business_name,
            "city": t.city,
            "connected_lines_count": len(lines),
            "whatsapp_lines": lines
        })

    return output
