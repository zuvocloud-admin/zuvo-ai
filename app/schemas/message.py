from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class OutboundTextMessageRequest(BaseModel):
    recipient_phone: str = Field(..., description="E.164 formatted customer phone number (e.g. 919414099999)")
    message_text: str = Field(..., description="Text content to send")
    sender_number_id: Optional[str] = Field(None, description="ZuvoCloud whatsapp_number ID or Meta phone_number_id")


class InboundMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    whatsapp_number_id: str
    worker_id: Optional[str] = None
    worker_name: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: str
    direction: str
    raw_content: str
    parsed_intent: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime


class MessageDispatchResult(BaseModel):
    success: bool
    wamid: Optional[str] = None
    recipient_phone: str
    meta_response: Optional[dict] = None
    error_message: Optional[str] = None


class SimulateInboundRequest(BaseModel):
    phone_number_id: str = Field(..., description="Target WhatsApp Phone Number ID (or Zuvo whatsapp_number ID)")
    sender_phone: str = Field(..., description="Customer phone number")
    sender_name: str = Field(..., description="Customer display name")
    message_text: str = Field(..., description="Message text content")

