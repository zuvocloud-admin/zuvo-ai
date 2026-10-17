from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class TextContent(BaseModel):
    body: str


class AudioContent(BaseModel):
    id: str
    mime_type: Optional[str] = None


class ImageContent(BaseModel):
    id: str
    mime_type: Optional[str] = None
    caption: Optional[str] = None


class WebhookMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    type: str = "text"
    text: Optional[TextContent] = None
    audio: Optional[AudioContent] = None
    image: Optional[ImageContent] = None


class ContactProfile(BaseModel):
    name: Optional[str] = None


class Contact(BaseModel):
    profile: Optional[ContactProfile] = None
    wa_id: str


class Metadata(BaseModel):
    display_phone_number: Optional[str] = None
    phone_number_id: str


class Value(BaseModel):
    messaging_product: Optional[str] = "whatsapp"
    metadata: Optional[Metadata] = None
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[WebhookMessage]] = None
    statuses: Optional[List[Dict[str, Any]]] = None


class Change(BaseModel):
    value: Value
    field: Optional[str] = "messages"


class Entry(BaseModel):
    id: str
    changes: List[Change]


class MetaWebhookPayload(BaseModel):
    object: Optional[str] = "whatsapp_business_account"
    entry: List[Entry]
