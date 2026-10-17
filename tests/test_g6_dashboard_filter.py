import pytest


@pytest.mark.asyncio
async def test_gate_g6_worker_isolation_and_customer_360_timeline(client, seeded_tenant):
    tenant_id = seeded_tenant["tenant"].id
    worker_1_id = seeded_tenant["worker_1"].id
    worker_2_id = seeded_tenant["worker_2"].id
    customer_phone = "+919414099999"

    # 1. Customer sends message to Worker 1 (Ramesh)
    p1 = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WABA_TEST_001",
            "changes": [{
                "field": "messages",
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "+919829011111", "phone_number_id": "TEST_PNID_001"},
                    "contacts": [{"profile": {"name": "Sharma Traders"}, "wa_id": customer_phone}],
                    "messages": [{"from": customer_phone, "id": "wamid.CHAT_TO_WORKER_1", "timestamp": "1724263200", "type": "text", "text": {"body": "Chat with Ramesh Counter"}}]
                }
            }]
        }]
    }
    await client.post("/api/v1/whatsapp/webhook", json=p1)

    # 2. SAME Customer sends message to Worker 2 (Suresh)
    p2 = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WABA_TEST_001",
            "changes": [{
                "field": "messages",
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "+919829022222", "phone_number_id": "TEST_PNID_002"},
                    "contacts": [{"profile": {"name": "Sharma Traders"}, "wa_id": customer_phone}],
                    "messages": [{"from": customer_phone, "id": "wamid.CHAT_TO_WORKER_2", "timestamp": "1724263250", "type": "text", "text": {"body": "Chat with Suresh Field Rep"}}]
                }
            }]
        }]
    }
    await client.post("/api/v1/whatsapp/webhook", json=p2)

    # 3. TEST GATE G6: Worker-Level Isolation (Filter by Worker 1)
    res_w1 = await client.get("/api/v1/dashboard/feed", params={"tenant_id": tenant_id, "worker_id": worker_1_id})
    assert res_w1.status_code == 200
    data_w1 = res_w1.json()
    assert len(data_w1["messages"]) == 1
    assert data_w1["messages"][0]["worker_name"] == "Ramesh Sharma"
    assert data_w1["messages"][0]["content"] == "Chat with Ramesh Counter"

    # 4. TEST GATE G6: Worker-Level Isolation (Filter by Worker 2)
    res_w2 = await client.get("/api/v1/dashboard/feed", params={"tenant_id": tenant_id, "worker_id": worker_2_id})
    assert res_w2.status_code == 200
    data_w2 = res_w2.json()
    assert len(data_w2["messages"]) == 1
    assert data_w2["messages"][0]["worker_name"] == "Suresh Verma"
    assert data_w2["messages"][0]["content"] == "Chat with Suresh Field Rep"

    # 5. TEST GATE G6: Customer 360° Unified Timeline (Filter by Customer Phone)
    res_c360 = await client.get("/api/v1/dashboard/feed", params={"tenant_id": tenant_id, "customer_phone": customer_phone})
    assert res_c360.status_code == 200
    data_c360 = res_c360.json()
    # Must contain BOTH messages from Worker 1 and Worker 2 unified chronologically
    assert len(data_c360["messages"]) == 2
    contents = [m["content"] for m in data_c360["messages"]]
    assert "Chat with Ramesh Counter" in contents
    assert "Chat with Suresh Field Rep" in contents
