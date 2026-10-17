# ZuvoCloud AI Solution
## Modular Multi-Worker WhatsApp AI Operations Platform

ZuvoCloud is a multi-tenant, microservices-ready WhatsApp AI Operations platform engineered for Indian wholesale distributors and trading hubs (Sitapura / VKI / Mansarovar $\rightarrow$ Pan-India SME distribution).

It enables wholesale businesses to capture, attribute, and route high-volume WhatsApp commerce across multiple staff lines (Counter Sales, Field Reps, Godown Dispatch) into a centralized Owner Command Center without forcing workers to learn new software.

---

## 1. Architectural Highlights

* **SOLID Design Principles:** Strictly decoupled bounded contexts:
  * `SecurityService`: HMAC-SHA256 signature verification & PII masking.
  * `IdempotencyCache`: Distributed Redis / in-memory deduplication of Meta `wamid`.
  * `RouterService`: Deterministic resolution of `phone_number_id` $\to$ `worker_id` $\to$ `tenant_id`.
  * `IngestionService`: Asynchronous webhook ingestion and normalized message persistence.
  * `MetaWhatsAppClient`: Abstract `BaseMessagingClient` handling 24-hr session and template dispatches.
  * `DashboardService`: Gate G6 multi-worker filtering and Customer 360° unified historical thread.
* **Config-Driven Architecture:** Unified `config/config.yaml` with environment variable overrides via Pydantic `BaseSettings`. Zero hardcoded secrets.
* **Database Agnostic:** Works with **PostgreSQL + AsyncPG** in Docker/Production and **Async SQLite (`aiosqlite`)** for zero-dependency local testing.
* **Docker Compose Deployment:** Production-ready multi-container stack (`fastapi`, `postgres:16-alpine`, `redis:7-alpine`).

---

## 2. Directory Structure

```
zuvo-ai/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entrypoint & lifespan
│   ├── core/                       # Cross-cutting infrastructure
│   │   ├── config.py               # Pydantic BaseSettings + YAML loader
│   │   ├── security.py             # HMAC-SHA256 verification & PII masking
│   │   ├── database.py             # Async SQLAlchemy engine & session factory
│   │   ├── redis.py                # Redis client & idempotency helper
│   │   └── logging.py              # Structured logging configuration
│   ├── models/                     # SQLAlchemy Declarative Models
│   │   ├── tenant.py               # Multi-tenant workspace model
│   │   ├── user.py                 # Users & Worker roles (Owner, Manager, Worker)
│   │   ├── whatsapp_number.py      # Meta phone_number_id mapping model
│   │   ├── customer.py             # Customer profile, ledger & credit limits
│   │   ├── conversation.py         # Thread between customer & worker line
│   │   ├── message.py              # Inbound/Outbound message entity
│   │   └── audit_log.py            # Immutable audit trail
│   ├── schemas/                    # Pydantic Schemas & DTOs
│   │   ├── webhook.py              # Meta Cloud API Webhook payload models
│   │   ├── message.py              # Inbound & Outbound message DTOs
│   │   └── dashboard.py            # Gate G6 Dashboard & Worker feed DTOs
│   ├── services/                   # Business Logic & Orchestration
│   │   ├── router_service.py       # Single-webhook multi-number resolver
│   │   ├── ingestion_service.py    # Webhook ingestion pipeline
│   │   ├── whatsapp_client.py      # Outbound Meta Graph API client
│   │   ├── dashboard_service.py    # Gate G6 filtering & analytics engine
│   │   └── audit_service.py        # Immutable audit logging service
│   └── api/v1/                     # API Controllers
│       ├── router.py               # API v1 Router aggregator
│       ├── webhook.py              # GET (Handshake) & POST (Ingestion)
│       ├── messages.py             # Outbound dispatch & Simulation
│       ├── dashboard.py            # Owner Command Center & Tenant feed
│       └── health.py               # Health & Diagnostics
├── config/
│   └── config.yaml                 # Base configuration file
├── scripts/
│   ├── seed_data.py                # Seeds Jaipur distributor + 5 worker numbers
│   └── test_webhook_simulation.py  # Simulates multi-worker inbound traffic
├── tests/
│   ├── conftest.py                 # Pytest async fixtures (in-memory DB)
│   ├── test_webhook.py             # Handshake & Ingestion tests
│   ├── test_multi_number_routing.py# Multi-number attribution tests
│   └── test_g6_dashboard_filter.py # Gate G6 Worker & Customer 360° tests
├── Dockerfile                      # Production container build
├── docker-compose.yml              # Microservice stack (API + Postgres + Redis)
├── requirements.txt                # Python dependencies
└── .env.example                    # Environment variable template
```

---

## 3. Quickstart & Local Execution

### Option A: Local Python Development
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed Jaipur test distributor (1 Tenant, 1 Owner, 5 Workers, 3 Customers)
python scripts/seed_data.py

# 3. Run automated tests (100% Pass)
python -m pytest tests/ -v

# 4. Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at: **`http://localhost:8000/docs`**

---

### Option B: Docker Compose Microservices Deployment
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Launch full stack (FastAPI + PostgreSQL 16 + Redis 7)
docker compose up -d --build

# 3. Verify health
curl http://localhost:8000/api/v1/health
```

---

## 4. API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Healthcheck for DB, Redis, and App |
| `GET` | `/api/v1/whatsapp/webhook` | Meta Webhook Verification challenge handshake |
| `POST` | `/api/v1/whatsapp/webhook` | Meta Inbound Webhook event ingestion |
| `POST` | `/api/v1/messages/send` | Send outbound WhatsApp message via Meta Graph API |
| `POST` | `/api/v1/messages/simulate-inbound` | Simulate customer message to test worker routing |
| `GET` | `/api/v1/dashboard/feed` | Owner Command Center feed (Gate G6 filtering) |
| `GET` | `/api/v1/dashboard/tenants` | List registered business tenants & worker lines |

---

## 5. Gate G6 Verification (Multi-Worker Isolation vs Customer 360°)

* **Worker-Level Isolation:**
  `GET /api/v1/dashboard/feed?tenant_id={id}&worker_id={worker_id}`  
  $\implies$ Returns only messages handled on that worker's assigned WhatsApp line.
* **Customer 360° Unified Timeline:**
  `GET /api/v1/dashboard/feed?tenant_id={id}&customer_phone=+919414099999`  
  $\implies$ Aggregates all interactions the customer had across all 5 staff numbers into one chronological timeline.
