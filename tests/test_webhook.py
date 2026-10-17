import pytest
from app.core.config import settings


@pytest.mark.asyncio
async def test_webhook_verification_handshake_success(client):
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": settings.whatsapp.verify_token,
        "hub.challenge": "1158201244"
    }
    response = await client.get("/api/v1/whatsapp/webhook", params=params)
    assert response.status_code == 200
    assert response.text == "1158201244"


@pytest.mark.asyncio
async def test_webhook_verification_handshake_invalid_token(client):
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "wrong_invalid_token_123",
        "hub.challenge": "1158201244"
    }
    response = await client.get("/api/v1/whatsapp/webhook", params=params)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_inbound_webhook_event_ingestion(client, seeded_tenant):
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_TEST_001",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+919829011111",
                                "phone_number_id": "TEST_PNID_001"
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Sharma Traders"},
                                    "wa_id": "+919414099999"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "+919414099999",
                                    "id": "wamid.TEST_MSG_001",
                                    "timestamp": "1724263200",
                                    "type": "text",
                                    "text": {"body": "Sharma Traders ko 50 box pipe kal bhej do"}
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    response = await client.post("/api/v1/whatsapp/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["messages_processed_count"] == 1
    assert data["details"][0]["worker_name"] == "Ramesh Sharma"
    assert data["details"][0]["content"] == "Sharma Traders ko 50 box pipe kal bhej do"


@pytest.mark.asyncio
async def test_inbound_webhook_status_update_ignored_safely(client, seeded_tenant):
    """
    Validates that status update webhooks (e.g. sent, delivered, read) without messages
    are handled safely without error.
    """
    status_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_TEST_001",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+919829011111",
                                "phone_number_id": "TEST_PNID_001"
                            },
                            "statuses": [
                                {
                                    "id": "wamid.TEST_MSG_001",
                                    "status": "delivered",
                                    "timestamp": "1724263205",
                                    "recipient_id": "+919414099999"
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    response = await client.post("/api/v1/whatsapp/webhook", json=status_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["messages_processed_count"] == 0


@pytest.mark.asyncio
async def test_inbound_webhook_duplicate_dropped(client, seeded_tenant):
    """
    Validates idempotency: when the exact same message ID is re-sent, it is dropped.
    """
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_TEST_001",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+919829011111",
                                "phone_number_id": "TEST_PNID_001"
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Sharma Traders"},
                                    "wa_id": "+919414099999"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "+919414099999",
                                    "id": "wamid.IDEMPOTENT_TEST_999",
                                    "timestamp": "1724263210",
                                    "type": "text",
                                    "text": {"body": "Testing idempotency deduplication"}
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    # 1st time -> Processed
    res1 = await client.post("/api/v1/whatsapp/webhook", json=payload)
    assert res1.status_code == 200
    assert res1.json()["messages_processed_count"] == 1

    # 2nd time -> Dropped as duplicate
    res2 = await client.post("/api/v1/whatsapp/webhook", json=payload)
    assert res2.status_code == 200
    assert res2.json()["messages_processed_count"] == 0
