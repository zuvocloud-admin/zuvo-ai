import pytest


@pytest.mark.asyncio
async def test_multi_number_to_multi_worker_attribution(client, seeded_tenant):
    """
    Validates that a single webhook correctly routes:
    - Message on PNID_001 -> Worker Ramesh
    - Message on PNID_002 -> Worker Suresh
    """
    # 1. Send to Number 1 (Ramesh)
    payload_1 = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_TEST_001",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "+919829011111", "phone_number_id": "TEST_PNID_001"},
                            "contacts": [{"profile": {"name": "Customer A"}, "wa_id": "+919414011111"}],
                            "messages": [{"from": "+919414011111", "id": "wamid.MSG_TO_RAMESH", "timestamp": "1724263200", "type": "text", "text": {"body": "Order for counter"}}]
                        }
                    }
                ]
            }
        ]
    }
    res_1 = await client.post("/api/v1/whatsapp/webhook", json=payload_1)
    assert res_1.status_code == 200
    data_1 = res_1.json()
    assert data_1["details"][0]["worker_name"] == "Ramesh Sharma"
    assert data_1["details"][0]["whatsapp_line"] == "+919829011111"

    # 2. Send to Number 2 (Suresh)
    payload_2 = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_TEST_001",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "+919829022222", "phone_number_id": "TEST_PNID_002"},
                            "contacts": [{"profile": {"name": "Customer B"}, "wa_id": "+919414022222"}],
                            "messages": [{"from": "+919414022222", "id": "wamid.MSG_TO_SURESH", "timestamp": "1724263205", "type": "text", "text": {"body": "Field sample request"}}]
                        }
                    }
                ]
            }
        ]
    }
    res_2 = await client.post("/api/v1/whatsapp/webhook", json=payload_2)
    assert res_2.status_code == 200
    data_2 = res_2.json()
    assert data_2["details"][0]["worker_name"] == "Suresh Verma"
    assert data_2["details"][0]["whatsapp_line"] == "+919829022222"


@pytest.mark.asyncio
async def test_idempotency_deduplication(client, seeded_tenant):
    """
    Validates that re-sending the same wamid drops the duplicate and does not create duplicate records.
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
                            "metadata": {"display_phone_number": "+919829011111", "phone_number_id": "TEST_PNID_001"},
                            "contacts": [{"profile": {"name": "Customer Dup"}, "wa_id": "+919414099999"}],
                            "messages": [{"from": "+919414099999", "id": "wamid.UNIQUE_DUP_TEST_001", "timestamp": "1724263200", "type": "text", "text": {"body": "Duplicate test message"}}]
                        }
                    }
                ]
            }
        ]
    }

    # First send -> Processed
    res_first = await client.post("/api/v1/whatsapp/webhook", json=payload)
    assert res_first.status_code == 200
    assert res_first.json()["messages_processed_count"] == 1

    # Second send with same wamid -> Dropped (0 processed)
    res_second = await client.post("/api/v1/whatsapp/webhook", json=payload)
    assert res_second.status_code == 200
    assert res_second.json()["messages_processed_count"] == 0
