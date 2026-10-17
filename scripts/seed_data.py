import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import select
from app.core.database import AsyncSessionFactory, init_db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.whatsapp_number import WhatsAppNumber
from app.models.customer import Customer
from app.core.logging import logger, setup_logging


async def seed():
    setup_logging()
    await init_db()

    async with AsyncSessionFactory() as db:
        # Check if already seeded
        res = await db.execute(select(Tenant).where(Tenant.business_name == "Jaipur Hardware & Sanitary Distributors"))
        existing_tenant = res.scalar_one_or_none()
        
        workers_data = [
            ("Ramesh Sharma", "+15556751665", "1312713255253790", "Counter Sales & Billing (Meta Test Line)"),
            ("Suresh Verma", "+919829022222", "PNID_002", "Field Sales Rep (VKI & Sitapura)"),
            ("Mukesh Saini", "+919829033333", "PNID_003", "Godown & Vehicle Dispatch"),
            ("Deepak Gupta", "+919829044444", "PNID_004", "Accounts & Payment Recovery"),
            ("Amit Joshi", "+919829055555", "PNID_005", "Customer Complaints & Support")
        ]

        if existing_tenant:
            logger.info(f"Tenant already exists with ID: {existing_tenant.id}. Ensuring Meta Phone Number IDs are up to date...")
            # Check or update WhatsApp numbers for existing tenant
            for name, phone, pnid, designation in workers_data:
                wn_res = await db.execute(
                    select(WhatsAppNumber).where(
                        WhatsAppNumber.tenant_id == existing_tenant.id,
                        (WhatsAppNumber.meta_phone_number_id == pnid) | (WhatsAppNumber.display_name.like(f"%{name}%"))
                    )
                )
                existing_wn = wn_res.scalar_one_or_none()
                if existing_wn:
                    existing_wn.meta_phone_number_id = pnid
                    existing_wn.display_phone_number = phone
                    existing_wn.display_name = f"{name} ({designation})"
                    existing_wn.status = "ACTIVE"
                else:
                    # Find user
                    u_res = await db.execute(select(User).where(User.tenant_id == existing_tenant.id, User.full_name == name))
                    user = u_res.scalar_one_or_none()
                    if user:
                        db.add(WhatsAppNumber(
                            tenant_id=existing_tenant.id,
                            assigned_user_id=user.id,
                            meta_phone_number_id=pnid,
                            display_phone_number=phone,
                            display_name=f"{name} ({designation})",
                            status="ACTIVE"
                        ))
            await db.commit()
            logger.info("WhatsApp numbers updated successfully!")
            return existing_tenant.id

        # 1. Create Business Tenant

        created_workers = []
        for name, phone, pnid, designation in workers_data:
            worker = User(
                tenant_id=tenant.id,
                full_name=name,
                phone_number=phone,
                role="WORKER",
                designation=designation
            )
            db.add(worker)
            await db.flush()

            # Map WhatsApp line to Worker
            wa_num = WhatsAppNumber(
                tenant_id=tenant.id,
                assigned_user_id=worker.id,
                meta_phone_number_id=pnid,
                display_phone_number=phone,
                display_name=f"{name} ({designation})",
                status="ACTIVE"
            )
            db.add(wa_num)
            created_workers.append(worker)

        # 4. Create Initial Customers
        customers_data = [
            ("Sharma Traders VKI", "Pawan Sharma", "+919414099999", 150000.0, 45000.0),
            ("Khandelwal Sanitary Mansarovar", "Sunil Khandelwal", "+919414088888", 200000.0, 110000.0),
            ("Rajputana Electricals Sitapura", "Bhawani Singh", "+919414077777", 100000.0, 12000.0)
        ]

        for company, contact, phone, cr_limit, outstanding in customers_data:
            cust = Customer(
                tenant_id=tenant.id,
                company_name=company,
                contact_person=contact,
                primary_phone=phone,
                credit_limit=cr_limit,
                current_outstanding=outstanding
            )
            db.add(cust)

        await db.commit()
        logger.info(f"Database seeded successfully with 1 Tenant, 1 Owner, 5 Workers, 5 WhatsApp Lines, and 3 Customers!")
        return tenant.id


if __name__ == "__main__":
    asyncio.run(seed())
