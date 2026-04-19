# QRTifact

![QRTifact](qrtifactuz.jpg)

> Multilingual museum exhibit platform for Uzbekistan — visitors scan QR codes to explore exhibits in Uzbek, Russian, or English.

---

## About

QRTifact is a production-ready backend platform that connects museum visitors with exhibit content through QR codes. Museums register their exhibits with multilingual descriptions, images, and audio guides. Visitors scan a QR code and instantly access rich content in their preferred language.

---

## Features

- **QR Code Generation** — each exhibit gets a unique QR code generated automatically
- **Multilingual Content** — full support for Uzbek, Russian, and English (uz / ru / en)
- **Audio Guides** — per-language audio tracks for each exhibit
- **Media Gallery** — image and video support per exhibit
- **Google OAuth2** — sign in with Google
- **JWT Authentication** — secure access & refresh token flow
- **Admin Panel** — built-in sqladmin panel with Uzbek/Russian/English UI translation
- **Museum Hierarchy** — Country → City → Museum → Hall → Exhibit
- **Scan Credits** — visitors purchase scan credit packages to unlock exhibits
- **Payment Integration** — Payme & Click (Uzbek payment providers), Stripe planned
- **Favorites** — users can save and sync favorite exhibits
- **Analytics** — views and listens tracking per exhibit
- **File Storage** — AWS S3 for production, local fallback for development
- **Background Tasks** — Celery workers for QR generation, emails, audio processing

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI + Python 3.12 |
| Database | PostgreSQL 16 (async, SQLAlchemy 2.0) |
| Cache / Broker | Redis 7 |
| Background Tasks | Celery |
| File Storage | AWS S3 |
| Auth | JWT + Google OAuth2 |
| Payments | Payme, Click |
| Package Manager | uv |
| Containerization | Docker + Docker Compose |
| Reverse Proxy | Nginx |
| CI/CD | GitHub Actions → AWS EC2 |

---

## API

Interactive API documentation available at:

- **Swagger UI** → `http://your-domain/docs`
- **ReDoc** → `http://your-domain/redoc`
- **Admin Panel** → `http://your-domain/admin`
- **Health Check** → `http://your-domain/health`

### Main Endpoints

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/google
GET    /api/v1/exhibits
GET    /api/v1/exhibits/{slug}
GET    /api/v1/museums
POST   /api/v1/scans/access
POST   /api/v1/billing/orders
```

---

## Architecture

```
app/
├── api/v1/          ← Route handlers
├── core/            ← Config, DB, security, exceptions
├── models/          ← SQLAlchemy ORM models
├── schemas/         ← Pydantic v2 request/response schemas
├── services/        ← Business logic
└── tasks/           ← Celery background tasks
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
SECRET_KEY=
DATABASE_URL=
REDIS_URL=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
FRONTEND_URL=
BACKEND_URL=
ADMIN_USERNAME=
ADMIN_PASSWORD=
ADMIN_SECRET_KEY=
```

---

## License

MIT
