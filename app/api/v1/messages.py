from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.whatsapp_number import WhatsAppNumber
from app.models.customer import Customer
from app.models.conversation import Conversation
from app.models.message import Message
from typing import Optional
from app.schemas.message import OutboundTextMessageRequest, MessageDispatchResult, SimulateInboundRequest
from app.schemas.webhook import MetaWebhookPayload, Entry, Change, Value, Metadata, Contact, ContactProfile, WebhookMessage, TextContent
from app.services.whatsapp_client import whatsapp_client
from app.services.ingestion_service import IngestionService
from app.services.audit_service import AuditService
from app.core.logging import logger

router = APIRouter(prefix="/messages", tags=["Messages & Dispatch"])


@router.post("/send", response_model=MessageDispatchResult, summary="Send Outbound WhatsApp Message")
async def send_outbound_message(
    req: OutboundTextMessageRequest,
    tenant_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Sends an outbound WhatsApp message to a customer and persists it to the conversation thread.
    """
    # 1. Resolve Tenant & Sender Line
    if not tenant_id:
        if req.sender_number_id:
            wn_find = await db.execute(
                select(WhatsAppNumber).where(
                    (WhatsAppNumber.id == req.sender_number_id) | (WhatsAppNumber.meta_phone_number_id == req.sender_number_id)
                )
            )
            found_wn = wn_find.scalar_one_or_none()
            if found_wn:
                tenant_id = found_wn.tenant_id
        
        if not tenant_id:
            t_res = await db.execute(select(Tenant).where(Tenant.is_active == True).limit(1))
            first_t = t_res.scalar_one_or_none()
            if first_t:
                tenant_id = first_t.id
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active business tenant found")

    stmt = select(WhatsAppNumber).where(WhatsAppNumber.tenant_id == tenant_id, WhatsAppNumber.status == "ACTIVE")
    if req.sender_number_id:
        stmt = stmt.where(
            (WhatsAppNumber.id == req.sender_number_id) | (WhatsAppNumber.meta_phone_number_id == req.sender_number_id)
        )
    
    res = await db.execute(stmt)
    wa_number = res.scalars().first()

    if not wa_number:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active sender WhatsApp line not found for tenant")

    # Standardize recipient phone format
    clean_phone = req.recipient_phone.replace(" ", "").replace("-", "").strip()
    clean_with_plus = clean_phone if clean_phone.startswith("+") else f"+{clean_phone}"
    clean_without_plus = clean_phone.replace("+", "")

    # 2. Dispatch via Meta WhatsApp Client
    dispatch_res = await whatsapp_client.send_text_message(
        phone_number_id=wa_number.meta_phone_number_id,
        recipient_phone=clean_without_plus,
        text_body=req.message_text
    )

    if not dispatch_res.success:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=dispatch_res.error_message or "Failed to dispatch message")

    # 3. Resolve Customer & Conversation
    stmt_cust = select(Customer).where(
        Customer.tenant_id == tenant_id,
        (Customer.primary_phone == clean_phone) | 
        (Customer.primary_phone == clean_with_plus) | 
        (Customer.primary_phone == clean_without_plus)
    )
    res_cust = await db.execute(stmt_cust)
    customer = res_cust.scalar_one_or_none()

    if not customer:
        customer = Customer(
            tenant_id=tenant_id,
            company_name=f"Customer {clean_phone}",
            primary_phone=clean_phone
        )
        db.add(customer)
        await db.flush()

    stmt_conv = select(Conversation).where(
        Conversation.whatsapp_number_id == wa_number.id,
        (Conversation.customer_phone == clean_phone) | 
        (Conversation.customer_phone == clean_with_plus) | 
        (Conversation.customer_phone == clean_without_plus)
    )
    res_conv = await db.execute(stmt_conv)
    conv = res_conv.scalar_one_or_none()

    if not conv:
        conv = Conversation(
            tenant_id=tenant_id,
            whatsapp_number_id=wa_number.id,
            customer_id=customer.id,
            customer_phone=clean_phone,
            status="OPEN",
            last_message_at=datetime.utcnow()
        )
        db.add(conv)
        await db.flush()
    else:
        conv.last_message_at = datetime.utcnow()

    # 4. Store Outbound Message Record
    wamid = dispatch_res.wamid or f"wamid.OUT_{int(datetime.utcnow().timestamp())}"
    db_msg = Message(
        tenant_id=tenant_id,
        conversation_id=conv.id,
        whatsapp_number_id=wa_number.id,
        customer_id=customer.id,
        wamid=wamid,
        direction="OUTBOUND",
        sender_phone=wa_number.display_phone_number,
        recipient_phone=clean_phone,
        message_type="text",
        raw_content=req.message_text,
        status="SENT"
    )
    db.add(db_msg)
    
    # 5. Audit Log
    await AuditService.log_event(
        db=db,
        tenant_id=tenant_id,
        actor_type="USER",
        action="DISPATCH_OUTBOUND_MESSAGE",
        entity_type="message",
        entity_id=db_msg.id,
        details={"to": clean_phone, "content": req.message_text[:100], "wamid": wamid}
    )

    await db.commit()
    return dispatch_res


@router.post("/simulate-inbound", summary="Simulate Inbound Customer WhatsApp Message (Testing)")
async def simulate_inbound_message(
    req: SimulateInboundRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Helper endpoint to simulate an inbound Meta WhatsApp webhook payload.
    Useful for testing Gate G6 and multi-worker routing without active Meta webhook callbacks.
    """
    simulated_wamid = f"wamid.SIM_{req.sender_phone}_{int(datetime.utcnow().timestamp() * 1000)}"
    
    simulated_payload = MetaWebhookPayload(
        object="whatsapp_business_account",
        entry=[
            Entry(
                id="WHATSAPP_BUSINESS_ACCOUNT_ID_SIM",
                changes=[
                    Change(
                        field="messages",
                        value=Value(
                            messaging_product="whatsapp",
                            metadata=Metadata(
                                display_phone_number="+91-TEST-LINE",
                                phone_number_id=req.phone_number_id
                            ),
                            contacts=[
                                Contact(
                                    profile=ContactProfile(name=req.sender_name),
                                    wa_id=req.sender_phone
                                )
                            ],
                            messages=[
                                WebhookMessage(
                                    from_=req.sender_phone,
                                    id=simulated_wamid,
                                    timestamp=str(int(datetime.utcnow().timestamp())),
                                    type="text",
                                    text=TextContent(body=req.message_text)
                                )
                            ]
                        )
                    )
                ]
            )
        ]
    )

    results = await IngestionService.process_webhook_payload(db, simulated_payload)
    return {"status": "ok", "simulated_wamid": simulated_wamid, "details": results}
