from fastapi import APIRouter, Depends, Request, Response, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.core.security import SecurityService
from app.core.logging import logger
from app.schemas.webhook import MetaWebhookPayload
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/whatsapp", tags=["Meta WhatsApp Webhook"])


@router.get("/webhook", summary="Meta Webhook Verification Handshake")
async def verify_webhook(request: Request):
    """
    Handles Meta's initial webhook handshake validation.
    Verifies hub.verify_token against configured META_VERIFY_TOKEN.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.whatsapp.verify_token:
            logger.info("Meta Webhook Verification handshake SUCCESS.")
            # Return challenge as plain text integer
            return Response(content=challenge, media_type="text/plain", status_code=status.HTTP_200_OK)
        else:
            logger.warning(f"Meta Webhook Verification failed. Token mismatch: received '{token}'")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch")

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing verification query parameters")


@router.post("/webhook", summary="Inbound WhatsApp Event Receiver")
async def receive_webhook_event(
    request: Request,
    payload: MetaWebhookPayload,
    db: AsyncSession = Depends(get_db),
    x_hub_signature_256: str = Header(None)
):
    """
    Receives and processes inbound Meta WhatsApp Cloud API webhooks.
    Validates HMAC signature, deduplicates via wamid, maps worker, and stores message.
    """
    logger.info("WhatsApp webhook received")

    # 1. Validate HMAC signature
    raw_body = await request.body()
    is_valid_sig = SecurityService.verify_meta_signature(raw_body, x_hub_signature_256)
    if not is_valid_sig:
        logger.warning("Rejected webhook due to invalid HMAC signature.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    # 2. Process message batch asynchronously through Ingestion Service
    try:
        results = await IngestionService.process_webhook_payload(db, payload)
        # Always return HTTP 200 to Meta to acknowledge receipt promptly
        return {"status": "ok", "messages_processed_count": len(results), "details": results}
    except Exception as e:
        logger.error(f"Error during webhook ingestion: {str(e)}", exc_info=True)
        # Still return 200 with status received to avoid continuous Meta retries
        return {"status": "error", "error_message": str(e)}
