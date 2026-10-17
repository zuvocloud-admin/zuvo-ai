# ZuvoCloud System Architecture & Technical Design

## 1. High-Level System Architecture

ZuvoCloud is built as an ambient operations layer that integrates directly into Meta's WhatsApp Cloud API. It provides real-time ingestion, worker attribution, and owner visibility without forcing sales workers or customers to adopt new software.

```
                                  ZUVOCLOUD SYSTEM TOPOLOGY
                                  
   +-----------------------------------------------------------------------------------------+
   |                             META WHATSAPP BUSINESS PLATFORM                             |
   |                                                                                         |
   |   Worker 1 (Counter)        Worker 2 (Field Rep)        Worker 3 (Godown)     Worker N  |
   |   [+91 98290-11111]         [+91 98290-22222]           [+91 98290-33333]        ...    |
   |   (Meta PNID_001)           (Meta PNID_002)             (Meta PNID_003)                 |
   +--------------------------------------------+--------------------------------------------+
                                                | Real-time HTTP Webhook Payload (JSON)
                                                v
   +-----------------------------------------------------------------------------------------+
   |                            ZUVOCLOUD FASTAPI INGESTION ENGINE                           |
   |                                                                                         |
   |   1. Security Layer        : Validates X-Hub-Signature-256 (HMAC-SHA256)                |
   |   2. Idempotency Layer     : Checks Redis SETNX with wamid (24h TTL) to drop duplicates |
   |   3. Router Service        : Maps phone_number_id -> worker_id -> tenant_id            |
   |   4. Customer Engine       : Resolves or auto-provisions Customer entity in tenant      |
   |   5. Conversation Thread   : Appends message to worker-customer conversation thread     |
   |   6. Immutable Audit Log   : Snapshots actor and payload into audit_logs table          |
   +--------------------------------------------+--------------------------------------------+
                                                |
                       +------------------------+------------------------+
                       |                                                 |
                       v                                                 v
   +---------------------------------------+   +---------------------------------------------+
   |       POSTGRESQL / SQLITE STORE       |   |           META GRAPH OUTBOUND API           |
   |                                       |   |                                             |
   | - tenants (UUID isolation)            |   | - 24-hr Freeform Session Text Dispatch      |
   | - users (Owner, Manager, Worker)      |   | - Pre-approved Utility Template Dispatch    |
   | - whatsapp_numbers (PNID mappings)    |   |                                             |
   | - customers (Ledger & Credit Limits)  |   +---------------------------------------------+
   | - conversations & messages            |
   | - audit_logs                          |
   +-------------------+-------------------+
                       |
                       v
   +-----------------------------------------------------------------------------------------+
   |                         OWNER COMMAND CENTER (GATE G6 ENGINE)                           |
   |                                                                                         |
   | • Worker-Level Isolation : Filter by worker_id -> Displays only that employee's feed    |
   | • Customer 360° View     : Filter by customer_phone -> Aggregates all 5 worker chats   |
   | • Real-time Metrics      : Inbound vs Outbound volume, active staff, credit alerts      |
   +-----------------------------------------------------------------------------------------+
```

---

## 2. SOLID Design Principles in Practice

| Principle | Architectural Implementation | Reference Module |
| :--- | :--- | :--- |
| **Single Responsibility (SRP)** | Each service has one and only one responsibility. `SecurityService` only handles HMAC and PII; `RouterService` only resolves phone IDs; `IdempotencyCache` only tracks message deduplication. | [`app/core/security.py`](file:///C:/js/zuvo-ai/app/core/security.py)<br>[`app/core/redis.py`](file:///C:/js/zuvo-ai/app/core/redis.py)<br>[`app/services/router_service.py`](file:///C:/js/zuvo-ai/app/services/router_service.py) |
| **Open/Closed (OCP)** | Outbound messaging adheres to `BaseMessagingClient`. New SMS or WhatsApp gateway adapters can be plugged in without changing the core webhook ingestion pipeline. | [`app/services/whatsapp_client.py`](file:///C:/js/zuvo-ai/app/services/whatsapp_client.py) |
| **Liskov Substitution (LSP)** | Storage layers work identically whether backed by SQLite in unit tests or PostgreSQL in Docker production. | [`app/core/database.py`](file:///C:/js/zuvo-ai/app/core/database.py) |
| **Interface Segregation (ISP)** | Schemas and DTOs are strictly partitioned: `MetaWebhookPayload`, `OutboundTextMessageRequest`, `DashboardFeedResponse`. | [`app/schemas/`](file:///C:/js/zuvo-ai/app/schemas/) |
| **Dependency Inversion (DIP)** | API route handlers depend on abstractions and rely on FastAPI's `Depends(get_db)` dependency injection rather than instantiating hard database sessions. | [`app/api/v1/`](file:///C:/js/zuvo-ai/app/api/v1/) |

---

## 3. Relational Database Schema (ER Overview)

```
   +----------------+           +-------------------+
   |    tenants     | 1       N |       users       |
   |----------------|-----------|-------------------|
   | id (PK)        |           | id (PK)           |
   | business_name  |           | tenant_id (FK)    |
   | gstin          |           | full_name         |
   | city           |           | role (OWNER/WORKER|
   +-------+--------+           +---------+---------+
           |                              |
           | 1                          1 |
           |                              |
           | N                          N |
   +-------+--------+           +---------+---------+
   |   customers    |           | whatsapp_numbers  |
   |----------------|           |-------------------|
   | id (PK)        |           | id (PK)           |
   | tenant_id (FK) |           | tenant_id (FK)    |
   | company_name   |           | assigned_user(FK) |
   | primary_phone  |           | meta_phone_number_id (Unique)
   | credit_limit   |           | display_number    |
   +-------+--------+           +---------+---------+
           |                              |
           | 1                          1 |
           |                              |
           | N                          N |
   +-------+------------------------------+---------+
   |                  conversations                 |
   |------------------------------------------------|
   | id (PK)                                        |
   | tenant_id (FK)                                 |
   | whatsapp_number_id (FK)                        |
   | customer_id (FK)                               |
   | status (OPEN / HELD / RESOLVED)                |
   +-----------------------+------------------------+
                           |
                           | 1
                           |
                           | N
   +-----------------------+------------------------+
   |                    messages                    |
   |------------------------------------------------|
   | id (PK)                                        |
   | tenant_id (FK)                                 |
   | conversation_id (FK)                           |
   | whatsapp_number_id (FK)                        |
   | customer_id (FK)                               |
   | wamid (Unique Meta Message ID)                 |
   | direction (INBOUND / OUTBOUND)                 |
   | sender_phone, recipient_phone                  |
   | message_type (text / audio / image)            |
   | raw_content                                    |
   | status (RECEIVED / PROCESSED / SENT)           |
   +------------------------------------------------+
```

---

## 4. Multi-Tenant Isolation & DPDP Act 2023 Compliance

1. **Logical Isolation at Query Level:**
   Every database query is scoped by `tenant_id`. Cross-tenant data leakage is structurally impossible.
2. **Data Residency & Localization:**
   Production workloads are deployed strictly inside Google Cloud Platform Mumbai region (`asia-south1`).
3. **PII Masking & Confidentiality:**
   Sensitive phone numbers and customer details are masked in debug logs (`SecurityService.mask_phone_number`).
4. **Immutable Audit Governance:**
   All critical state changes, approvals, and dispatches write immutable entries into `audit_logs`.
