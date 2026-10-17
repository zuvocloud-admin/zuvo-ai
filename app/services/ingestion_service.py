from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.webhook import MetaWebhookPayload, WebhookMessage, Metadata, Contact
from app.services.router_service import RouterService
from app.services.audit_service import AuditService
from app.core.redis import idempotency_cache
from app.core.security import SecurityService
from app.core.logging import logger


class IngestionService:
    """
    Main Orchestration Service for Inbound WhatsApp Message Webhooks.
    Handles deduplication, multi-worker attribution, persistence, and audit.
    """

    @staticmethod
    async def process_webhook_payload(
        db: AsyncSession,
        payload: MetaWebhookPayload
    ) -> List[dict]:
        """
        Processes a full Meta Webhook batch payload.
        Returns a summary list of processed message records.
        """
        processed_results = []

        for entry in payload.entry:
            for change in entry.changes:
                if change.field != "messages":
                    logger.debug(f"Ignoring non-messages webhook field: {change.field}")
                    continue

                val = change.value
                if not val.metadata:
                    logger.debug("Webhook change value missing metadata, skipping")
                    continue

                phone_number_id = val.metadata.phone_number_id
                
                # Safely handle delivery status updates (e.g. sent, delivered, read)
                if val.statuses:
                    for status_item in val.statuses:
                        status_id = status_item.get("id")
                        status_val = status_item.get("status")
                        logger.info(f"WhatsApp status update: Message ID: {status_id} | Status: {status_val} | Phone Number ID: {phone_number_id}")
                    if not val.messages:
                        continue

                # 1. Resolve Multi-Tenant & Worker Routing
                routing = await RouterService.resolve_routing(db, phone_number_id)
                if not routing:
                    logger.warning(f"Dropping message batch for unmapped Phone Number ID: {phone_number_id}")
                    continue

                tenant, worker, wa_number = routing

                # Process all contacts mapping
                contact_names = {}
                if val.contacts:
                    for c in val.contacts:
                        contact_names[c.wa_id] = (c.profile.name if c.profile else None) or "Unknown Customer"

                # Process each message in the batch
                if val.messages:
                    for msg in val.messages:
                        result = await IngestionService._ingest_single_message(
                            db=db,
                            tenant_id=tenant.id,
                            worker_id=worker.id if worker else None,
                            worker_name=worker.full_name if worker else None,
                            wa_number=wa_number,
                            msg=msg,
                            customer_display_name=contact_names.get(msg.from_, "Unknown Customer")
                        )
                        if result:
                            processed_results.append(result)

        await db.commit()
        return processed_results

    @staticmethod
    async def _ingest_single_message(
        db: AsyncSession,
        tenant_id: str,
        worker_id: Optional[str],
        worker_name: Optional[str],
        wa_number,
        msg: WebhookMessage,
        customer_display_name: str
    ) -> Optional[dict]:
        wamid = msg.id
        sender_phone = msg.from_
        msg_type = msg.type
        masked_phone = SecurityService.mask_phone_number(sender_phone)
        
        logger.info(
            f"WhatsApp incoming message: Phone Number ID: {wa_number.meta_phone_number_id} | "
            f"Message ID: {wamid} | Sender: {masked_phone} | Message type: {msg_type}"
        )

        # 2. Check Idempotency (Deduplication)
        is_dup = await idempotency_cache.is_duplicate(wamid)
        if is_dup:
            logger.info(f"Duplicate message dropped (Message ID: {wamid}) for Tenant={tenant_id}")
            return None

        # Extract message body
        text_content = ""
        if msg.text:
            text_content = msg.text.body
        elif msg.audio:
            text_content = "[VOICE_NOTE_AUDIO]"
            msg_type = "audio"
        elif msg.image:
            text_content = msg.image.caption or "[IMAGE_ATTACHMENT]"
            msg_type = "image"
        else:
            text_content = f"[{msg_type.upper()}_CONTENT]"

        # 3. Resolve or Auto-Create Customer Account
        stmt_cust = select(Customer).where(
            Customer.tenant_id == tenant_id,
            Customer.primary_phone == sender_phone
        )
        res_cust = await db.execute(stmt_cust)
        customer = res_cust.scalar_one_or_none()

        if not customer:
            customer = Customer(
                tenant_id=tenant_id,
                company_name=customer_display_name,
                primary_phone=sender_phone,
                credit_limit=50000.0,  # Default starting limit
                current_outstanding=0.0
            )
            db.add(customer)
            await db.flush()
            logger.info(f"Created new Customer record: '{customer.company_name}' ({masked_phone})")

        # 4. Resolve or Create Conversation Thread with this Worker's Number
        stmt_conv = select(Conversation).where(
            Conversation.whatsapp_number_id == wa_number.id,
            Conversation.customer_phone == sender_phone
        )
        res_conv = await db.execute(stmt_conv)
        conversation = res_conv.scalar_one_or_none()

        if not conversation:
            conversation = Conversation(
                tenant_id=tenant_id,
                whatsapp_number_id=wa_number.id,
                customer_id=customer.id,
                customer_phone=sender_phone,
                status="OPEN",
                last_message_at=datetime.utcnow()
            )
            db.add(conversation)
            await db.flush()
        else:
            conversation.last_message_at = datetime.utcnow()
            conversation.customer_id = customer.id

        # 5. Persist Normalized Message
        db_message = Message(
            tenant_id=tenant_id,
            conversation_id=conversation.id,
            whatsapp_number_id=wa_number.id,
            customer_id=customer.id,
            wamid=wamid,
            direction="INBOUND",
            sender_phone=sender_phone,
            recipient_phone=wa_number.display_phone_number,
            message_type=msg_type,
            raw_content=text_content,
            parsed_intent=None,
            status="RECEIVED"
        )
        db.add(db_message)
        await db.flush()

        # 6. Immutable Audit Log Entry
        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            actor_type="META_WEBHOOK",
            actor_id=sender_phone,
            action="INGEST_INBOUND_MESSAGE",
            entity_type="message",
            entity_id=db_message.id,
            details={
                "wamid": wamid,
                "worker_id": worker_id,
                "worker_name": worker_name,
                "whatsapp_line": wa_number.display_phone_number,
                "content_preview": text_content[:100]
            }
        )

        logger.info(f"Message processed successfully: ID={db_message.id} | WAMID={wamid} | Worker={worker_name or 'Unassigned'}")

        return {
            "message_id": db_message.id,
            "wamid": wamid,
            "tenant_id": tenant_id,
            "worker_id": worker_id,
            "worker_name": worker_name,
            "whatsapp_line": wa_number.display_phone_number,
            "customer_id": customer.id,
            "customer_name": customer.company_name,
            "customer_phone": sender_phone,
            "content": text_content,
            "created_at": db_message.created_at.isoformat()
        }
