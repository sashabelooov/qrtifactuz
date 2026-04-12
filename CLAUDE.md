# QRTifact Backend — Claude Code Context

## What is this project?
QRTifact is a production-ready FastAPI backend for a multilingual museum exhibit platform in Uzbekistan.
Museums add exhibits with QR codes. Visitors scan QR codes and see exhibit details (text + audio) in Uzbek, Russian, or English. Visitors buy scan credit packages to unlock exhibits.

---

## Tech Stack
| Layer | Tool |
|---|---|
| Framework | FastAPI + Python 3.12 |
| Database | PostgreSQL (async, SQLAlchemy 2.0 + asyncpg) |
| Migrations | Alembic |
| Cache / Broker | Redis |
| Background Tasks | Celery |
| File Storage | AWS S3 |
| Auth | JWT (access 60min / refresh 30d) + Google OAuth2 |
| Payments | Payme + Click (Uzbek providers), Stripe later |
| Package Manager | uv |
| Containerization | Docker + Docker Compose |
| Reverse Proxy | Nginx |
| CI/CD | GitHub Actions |

---

## Folder Structure
```
app/
├── main.py                        ← FastAPI app, all routers registered here
├── api/v1/
│   ├── auth/router.py
│   ├── artifacts/router.py        ← public exhibit endpoints
│   ├── admin/router.py            ← admin-only endpoints
│   ├── billing/router.py
│   ├── languages/router.py
│   ├── favorites/router.py
│   ├── upload/router.py
│   ├── profiles/router.py
│   └── scans/router.py
├── core/
│   ├── config.py                  ← Pydantic Settings (from .env)
│   ├── database.py                ← async engine + get_db() dependency
│   ├── security.py                ← JWT + password hashing
│   ├── dependencies.py            ← get_current_user, get_current_admin
│   └── exceptions.py              ← custom exception classes + handlers
├── models/                        ← SQLAlchemy ORM models (one file per domain)
├── schemas/                       ← Pydantic v2 request/response schemas
├── services/                      ← all business logic (called by routes)
└── tasks/
    ├── celery_app.py
    ├── qr_tasks.py
    ├── email_tasks.py
    └── audio_tasks.py
migrations/                        ← Alembic (env.py imports all models)
tests/
docker/
    ├── Dockerfile
    └── nginx.conf
.github/workflows/ci-cd.yml
```

---

## Architecture Rules (ALWAYS follow these)

### 1. Layering — strict separation of concerns
- **Route** → validates input/output shapes, calls service, returns response schema
- **Service** → all business logic, DB queries, raises AppExceptions
- **Model** → SQLAlchemy table definition only, no logic
- **Schema** → Pydantic v2 shapes only, no DB access
- Routes never import models directly. Services never return raw ORM objects — always return dicts or dataclasses that schemas can parse.

### 2. Async everywhere
- All DB calls use `await session.execute(...)`, `await session.commit()`, etc.
- Use `AsyncSession` from `sqlalchemy.ext.asyncio`
- All service methods are `async def`

### 3. Atomic counter updates — CRITICAL
Never do read-then-write for counters. Always use:
```python
await session.execute(
    update(Exhibit).where(Exhibit.id == id).values(views_count=Exhibit.views_count + 1)
)
```

### 4. Webhook safety
Always save raw payload to `PaymentWebhookEvent` BEFORE any processing:
```python
webhook_event = PaymentWebhookEvent(provider=provider, raw_payload=raw_body, ...)
session.add(webhook_event)
await session.commit()
# then process
```

### 5. Error handling
Only use custom exceptions from `app/core/exceptions.py`:
- `AppException` (base)
- `NotFoundException`
- `UnauthorizedException`
- `ForbiddenException`
- `BadRequestException`
- `InsufficientScansException`

Register all exception handlers in `main.py`.

### 6. Dependency injection
- DB session: `db: AsyncSession = Depends(get_db)`
- Auth: `current_user: User = Depends(get_current_user)`
- Admin: `current_user: User = Depends(get_current_admin)`

### 7. Schemas
- Use Pydantic v2 (`model_config = ConfigDict(from_attributes=True)`)
- Separate `Create`, `Update`, `Response` schemas per domain
- Never expose `hashed_password`, `google_id`, or internal fields in responses

---

## Database Models Quick Reference

| Model | Key Fields |
|---|---|
| User | id, email, phone, hashed_password, google_id, is_active, is_admin |
| Profile | user_id(FK), full_name, avatar_url, preferred_language |
| Museum | name, slug, description, address, city, country, logo_url, is_active |
| Hall | museum_id(FK), name, description, floor |
| Category | museum_id(FK), slug + CategoryTranslation(language, name, description) |
| Exhibit | museum_id, hall_id, category_id, created_by, slug, qr_code_url, status, views_count, listens_count |
| ExhibitTranslation | exhibit_id, language, title, description |
| ExhibitMedia | exhibit_id, storage_path, public_url, media_type, is_cover, sort_order |
| ExhibitAudioTrack | exhibit_id, language, storage_path, public_url, duration_seconds |
| Favorite | user_id + exhibit_id (unique constraint) |
| ScanOrder | user_id, scans_total, scans_left, price, status(pending/paid/failed) |
| ScanAccess | user_id, exhibit_id, order_id, expires_at |
| ScanEvent | user_id(nullable), exhibit_id, scanned_at |
| PaymentTransaction | user_id, order_id, provider, provider_transaction_id, amount, currency, status |
| PaymentWebhookEvent | provider, event_type, raw_payload(Text), is_processed |
| ListeningSession | user_id(nullable), audio_track_id, exhibit_id, duration_listened, started_at |
| AuditLog | user_id(nullable), action, entity, entity_id, detail |

Exhibit `status` enum: `draft | published | archived`
ScanOrder `status` enum: `pending | paid | failed`
Supported languages: `uz | ru | en`

---

## Key Business Logic

### Scan flow (credit deduction)
1. `POST /scans/access` — check if `ScanAccess` already exists for (user, exhibit)
2. If yes → return existing access (idempotent, no deduction)
3. If no → find `ScanOrder` with `scans_left > 0` (ordered by created_at ASC — use oldest first)
4. Atomically decrement: `UPDATE scan_orders SET scans_left = scans_left - 1 WHERE id = :id AND scans_left > 0`
5. Create `ScanAccess` record + `ScanEvent`
6. If no credits → raise `InsufficientScansException`

### QR code generation (Celery task)
1. Task receives `exhibit_id`
2. Generate QR code PNG → encode exhibit URL (frontend URL + exhibit slug)
3. Upload PNG to S3 under `qr/{exhibit_id}.png`
4. Update `exhibit.qr_code_url` with public S3 URL

### Google OAuth flow
1. `GET /auth/google` → build Google authorization URL → return `{"redirect_url": "..."}`
2. `GET /auth/google/callback?code=...` → exchange code → get user info from Google
3. Find user by `google_id` or `email` → create if not found
4. Return access + refresh tokens

---

## Celery Tasks

| File | Task | Trigger |
|---|---|---|
| qr_tasks.py | `generate_qr_code(exhibit_id)` | After exhibit created/published |
| email_tasks.py | `send_welcome_email(user_id)` | After user registration |
| audio_tasks.py | `process_audio(exhibit_id, track_id, s3_path)` | After audio uploaded |

---

## Running the Project
```bash
# First time setup
cp .env.example .env
# Fill in secrets in .env

# Start all services
docker compose up --build

# Run migrations
docker compose exec api uv run alembic revision --autogenerate -m "initial"
docker compose exec api uv run alembic upgrade head

# Run tests
docker compose exec api uv run pytest

# Celery worker (separate terminal)
docker compose exec worker uv run celery -A app.tasks.celery_app worker --loglevel=info
```

---

## Environment Variables (.env)
```
# App
SECRET_KEY=your-secret-key-min-32-chars
DEBUG=false

# Database
DATABASE_URL=postgresql+asyncpg://qrtifact:password@db:5432/qrtifact

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
ALGORITHM=HS256

# AWS S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=qrtifact
AWS_S3_REGION=us-east-1

# Google OAuth2
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

# Frontend
FRONTEND_URL=http://localhost:3000
```

---

## API Surface (all endpoints)

### Auth
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
GET    /api/v1/auth/google
GET    /api/v1/auth/google/callback
```

### Public Exhibits
```
GET    /api/v1/exhibits                  ?museum_id= &status= &category_id= &hall_id=
GET    /api/v1/exhibits/{slug}
POST   /api/v1/exhibits/{id}/view
POST   /api/v1/exhibits/{id}/listen
```

### Admin Exhibits
```
POST   /api/v1/admin/exhibits
PUT    /api/v1/admin/exhibits/{id}
DELETE /api/v1/admin/exhibits/{id}
PATCH  /api/v1/admin/exhibits/{id}/status
```

### Favorites
```
GET    /api/v1/favorites
POST   /api/v1/favorites              body: { exhibit_id }
DELETE /api/v1/favorites/{exhibit_id}
POST   /api/v1/favorites/sync         body: { exhibit_ids: [] }
```

### Upload
```
POST   /api/v1/upload/image
POST   /api/v1/upload/audio
```

### Reference Data
```
GET    /api/v1/museums
GET    /api/v1/museums/{id}
POST   /api/v1/admin/museums
GET    /api/v1/categories            ?museum_id=
GET    /api/v1/halls                 ?museum_id=
GET    /api/v1/languages
```

### Profiles
```
GET    /api/v1/profiles/{id}
PATCH  /api/v1/profiles/{id}
```

### Billing
```
GET    /api/v1/billing/packages
POST   /api/v1/billing/orders
POST   /api/v1/billing/webhook/payme
POST   /api/v1/billing/webhook/click
GET    /api/v1/billing/orders/{id}
```

### Scans
```
POST   /api/v1/scans/access
POST   /api/v1/scans/events
```

### Analytics (admin)
```
GET    /api/v1/admin/analytics/exhibits
```

---

## SQLAlchemy Conventions
- Use `Mapped[T]` and `mapped_column()` (SQLAlchemy 2.0 style)
- All tables use integer PKs except where noted
- `created_at` default: `server_default=func.now()`
- `updated_at`: `server_default=func.now(), onupdate=func.now()`
- Soft-delete is NOT used — hard deletes with cascade
- Index foreign keys explicitly
- Use `relationship()` with `lazy="selectin"` or `lazy="noload"` — never use lazy loading (async requirement)

## Alembic Convention
- `migrations/env.py` must import all models via `from app.models import *`
- `migrations/versions/` — never edit generated files by hand except for data migrations
- Always run `alembic upgrade head` before starting the app in production

## Testing Conventions
- Use `pytest-asyncio` with `asyncio_mode = "auto"`
- Use a separate test database (`TEST_DATABASE_URL` in env)
- Test each service method in isolation (mock DB session)
- Test each route via `httpx.AsyncClient` with the FastAPI test app
