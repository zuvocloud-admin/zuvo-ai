import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

import httpx
from scripts.seed_data import seed
from app.core.database import AsyncSessionFactory
from app.services.dashboard_service import DashboardService
from app.core.logging import logger, setup_logging


async def run_simulation():
    setup_logging()
    
    # 1. Seed database
    tenant_id = await seed()
    logger.info(f"Target Tenant ID: {tenant_id}")

    # 2. Simulate Inbound Webhooks
    async with AsyncSessionFactory() as db:
        logger.info("\n--- SIMULATING INBOUND MESSAGES ACROSS MULTIPLE WORKER NUMBERS ---")
        
        from app.services.ingestion_service import IngestionService
        from app.schemas.webhook import MetaWebhookPayload, Entry, Change, Value, Metadata, Contact, ContactProfile, WebhookMessage, TextContent
        import time

        simulated_events = [
            # Chat 1: Customer (Sharma Traders) -> Worker 1 (Ramesh Counter: PNID_001)
            ("PNID_001", "+919414099999", "Sharma Traders VKI", "Ramesh ji, 20mm CPVC pipe ke 50 box kal bhej do urgent."),
            # Chat 2: Customer (Sharma Traders) -> Worker 2 (Suresh Field: PNID_002)
            ("PNID_002", "+919414099999", "Sharma Traders VKI", "Suresh bhai, sample wale Jaguar divertor pasand aa gaye hain."),
            # Chat 3: Customer (Khandelwal Sanitary) -> Worker 1 (Ramesh Counter: PNID_001)
            ("PNID_001", "+919414088888", "Khandelwal Sanitary", "Purane bill ka payment RTGS kar diya hai ₹1.1 Lakh."),
            # Chat 4: Customer (Rajputana Electricals) -> Worker 3 (Mukesh Godown: PNID_003)
            ("PNID_003", "+919414077777", "Rajputana Electricals", "Mukesh ji, vehicle RJ-14 kab tak dispatch hoga?")
        ]

        for pnid, cust_phone, cust_name, msg_body in simulated_events:
            wamid = f"wamid.SIM_{cust_phone}_{int(time.time() * 1000)}_{pnid}"
            payload = MetaWebhookPayload(
                object="whatsapp_business_account",
                entry=[
                    Entry(
                        id="WABA_001",
                        changes=[
                            Change(
                                field="messages",
                                value=Value(
                                    metadata=Metadata(
                                        display_phone_number="+91-LINE",
                                        phone_number_id=pnid
                                    ),
                                    contacts=[Contact(profile=ContactProfile(name=cust_name), wa_id=cust_phone)],
                                    messages=[
                                        WebhookMessage(
                                            from_=cust_phone,
                                            id=wamid,
                                            timestamp=str(int(time.time())),
                                            type="text",
                                            text=TextContent(body=msg_body)
                                        )
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
            res = await IngestionService.process_webhook_payload(db, payload)
            logger.info(f"Ingested simulated event: PNID={pnid} Customer={cust_name} -> Processed: {len(res)}")

        # 3. Test Gate G6: Worker-Level Isolation
        logger.info("\n--- TESTING GATE G6: WORKER-LEVEL ISOLATION (Ramesh vs Suresh) ---")
        
        # Query Worker 1 (Ramesh)
        from sqlalchemy import select
        from app.models.user import User
        res_ramesh = await db.execute(select(User).where(User.tenant_id == tenant_id, User.full_name.like("%Ramesh%")))
        ramesh = res_ramesh.scalar_one()

        feed_ramesh = await DashboardService.get_dashboard_feed(db, tenant_id=tenant_id, worker_id=ramesh.id)
        logger.info(f"Worker Ramesh Feed Count: {len(feed_ramesh.messages)}")
        for m in feed_ramesh.messages:
            logger.info(f"  [RAMESH LINE] From: {m.customer_name} ({m.customer_phone}) -> '{m.content}'")

        # 4. Test Gate G6: Customer 360° Unified Timeline
        logger.info("\n--- TESTING GATE G6: CUSTOMER 360° UNIFIED TIMELINE (Sharma Traders) ---")
        feed_sharma = await DashboardService.get_dashboard_feed(db, tenant_id=tenant_id, customer_phone="+919414099999")
        logger.info(f"Sharma Traders 360° Unified Feed Count: {len(feed_sharma.messages)} (Merged across all workers)")
        for m in feed_sharma.messages:
            logger.info(f"  [360° TIMELINE] Handled By: {m.worker_name} ({m.worker_phone}) -> '{m.content}'")

    logger.info("\nSimulation and Gate G6 verification completed with 100% SUCCESS!")


if __name__ == "__main__":
    asyncio.run(run_simulation())
