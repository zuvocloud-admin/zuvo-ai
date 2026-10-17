from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class DashboardMessageItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    wamid: str
    direction: str
    sender_phone: str
    recipient_phone: str
    message_type: str
    content: str
    parsed_intent: Optional[str] = None
    confidence_score: Optional[float] = None
    worker_id: Optional[str] = None
    worker_name: Optional[str] = None
    worker_phone: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: str
    created_at: datetime


class WorkerSummary(BaseModel):
    worker_id: str
    worker_name: str
    designation: Optional[str] = None
    phone_number: str
    meta_phone_number_id: str
    total_messages_today: int
    active_conversations_count: int


class DashboardMetrics(BaseModel):
    tenant_id: str
    business_name: str
    total_messages_today: int
    total_inbound: int
    total_outbound: int
    active_workers_count: int
    active_customers_count: int
    pending_approvals_count: int


class DashboardFeedResponse(BaseModel):
    metrics: DashboardMetrics
    workers: List[WorkerSummary]
    messages: List[DashboardMessageItem]
    filter_applied: dict
