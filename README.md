# DoctorIn — Professional Networking & Discovery Platform for Doctors

> **"Connect with Verified Medical Professionals."**

DoctorIn is a purpose-built professional networking and discovery platform designed specifically for the medical ecosystem. Similar conceptually to LinkedIn, DoctorIn provides verified medical credential badges, doctor-to-doctor clinical networking, hospital organization management, healthcare recruitment, and patient-facing doctor discovery.

---

## 🛠 DoctorIn Technology Stack

The DoctorIn platform is built on modern, type-safe full-stack technologies:

### 1. Frontend
* **Framework**: [Next.js 14.2.3](https://nextjs.org/) (App Router architecture)
* **Library**: React 18
* **Language**: TypeScript 5.4 (Strict mode)
* **Styling**: Tailwind CSS 3.4 & PostCSS with curated medical color tokens
* **Icons**: Lucide React
* **Utility Libraries**: `clsx`, `tailwind-merge`
* **Development Server**: Next.js Hot Module Replacement (HMR) / Fast Refresh

### 2. Backend
* **Framework**: [FastAPI 0.110+](https://fastapi.tiangolo.com/) (Modular Monolith)
* **Language**: Python 3.14 / 3.12+
* **ASGI Server**: Uvicorn with development auto-reload (`--reload`)
* **Validation & Schemas**: Pydantic v2
* **ORM & Database Layer**: SQLAlchemy 2.0 (AsyncIO with `async_sessionmaker`)
* **Database Drivers**: `aiosqlite` (local development fallback), `asyncpg` (production PostgreSQL)
* **Database Migrations**: Alembic

### 3. Database & Caching
* **Local Development**: SQLite (`doctorin_dev.db`) via `sqlite+aiosqlite`
* **Production Database**: PostgreSQL 16 with `tsvector` full-text search indexing
* **Cache & Rate Limiting**: Redis 7 (OTP limits, token revocation, request throttling)

### 4. Authentication & Security
* **User Onboarding**: Unified default registration as standard `User` role
* **Multi-Role RBAC**: 4 user roles (`USER`, `DOCTOR`, `HOSPITAL_ADMIN`, `ADMIN`)
* **Tokens**: JWT (short-lived access tokens + 7-day rotating refresh tokens)
* **OTP Verification**: HMAC-SHA256 hashed OTPs, 5-minute TTL, 5-attempt lockout, 60-second cooldown
* **Email Delivery**: SMTP (TLS port 587) / Resend API / local console development logging
* **Security Middleware**: CORS whitelist, Request ID tracking, structured JSON logging, CSP, and HSTS headers

### 5. Document & Storage Security
* **Storage Provider**: S3-compatible object storage (AWS S3, MinIO)
* **Validation**: Whitelisted MIME types (`application/pdf`, `image/jpeg`, `image/png`) and 10MB size limit
* **Key Isolation**: Randomized UUID paths (`documents/{category}/{entity_id}/{uuid}.{ext}`) to prevent IDOR and directory traversal
* **Access Control**: Temporary presigned download URLs (15-minute TTL); raw storage buckets are never public

### 6. Testing & Quality Assurance
* **Backend Testing**: Pytest, pytest-asyncio, HTTPX async test client (53 integration, e2e, and unit tests)
* **Frontend Verification**: TypeScript type checking (`tsc --noEmit`)
* **Code Formatting & Linting**: Ruff (Python), Next Lint (ESLint)

---

## 📂 Project Structure

```text
DoctorIn/
│
├── frontend/                  # Next.js 14 Web Application
│   ├── src/
│   │   ├── app/               # Next.js App Router (auth, profile, verification, hospitals, admin)
│   │   ├── components/        # Reusable UI & Layout components (Navbar, Footer, Button, Badge)
│   │   ├── features/          # Domain feature components (auth, doctor, feed, messaging, search)
│   │   ├── lib/               # API client, utilities, constants
│   │   └── types/             # TypeScript interfaces and response schemas
│   ├── public/                # Static web assets
│   ├── package.json           # Frontend scripts & dependencies
│   ├── tailwind.config.ts     # Tailwind design system configuration
│   ├── tsconfig.json          # TypeScript compiler options
│   ├── .env.example           # Frontend environment variable template
│   └── Dockerfile             # Production multi-stage Docker build
│
├── backend/                   # FastAPI Modular Monolith
│   ├── app/
│   │   ├── api/               # API v1 routers & dependency injection
│   │   ├── core/              # Config, Security, Database, Redis, Storage, Logging
│   │   ├── models/            # SQLAlchemy database models (User, Doctor, Hospital, Verification)
│   │   ├── repositories/      # Data access layer repositories
│   │   ├── schemas/           # Pydantic v2 request & response schemas
│   │   ├── services/          # Core business logic services
│   │   └── main.py            # FastAPI application factory & lifespan
│   ├── alembic/               # Database migration scripts
│   ├── requirements/          # Dependency manifests (base.txt, dev.txt, test.txt)
│   ├── requirements.txt       # Root backend requirements pointer (-r requirements/base.txt)
│   ├── scripts/               # Maintenance scripts (init_db.py, backup_db.ps1)
│   ├── tests/                 # 53 unit, integration, and security test cases
│   ├── .env.example           # Backend environment variable template
│   ├── doctorin_dev.db        # Local SQLite development database (37 tables preserved)
│   └── Dockerfile             # Production multi-stage Docker build
│
├── docs/                      # Architectural and operational documentation
│   └── OPERATIONS.md          # Production operations guide
│
├── nginx/                     # Reverse proxy & TLS configuration
│   ├── conf.d/
│   └── nginx.conf
│
├── scripts/                   # Root automation & startup scripts
│   ├── dev.bat                # Windows Batch: start backend & frontend with auto-reload
│   ├── dev.ps1                # PowerShell: start backend & frontend with auto-reload
│   └── test.bat               # Run backend pytest & frontend typecheck
│
├── .env.example               # Root environment variable template
├── .gitignore                 # Git ignore rules for Python, Node, and environments
├── docker-compose.yml         # Local development container orchestration
├── docker-compose.prod.yml    # Production container configuration
├── Makefile                   # Developer CLI makefile
├── start-dev.bat              # Quick one-click development launcher
├── start-dev.ps1              # Quick PowerShell development launcher
└── README.md                  # Project documentation
```

---

## 💻 Installation & Setup

### Prerequisites
* **Python**: 3.12 or higher (Python 3.14 compatible)
* **Node.js**: v18.0.0 or higher (Node v24 tested)
* **npm**: v9.0.0 or higher

### 1. Environment Configuration
Copy the sample environment files:
```powershell
# In project root:
Copy-Item .env.example .env

# In frontend:
Copy-Item frontend\.env.example frontend\.env.local
```

### 2. Backend Installation
```powershell
cd d:\DoctorIn\backend
pip install -r requirements/base.txt
# For testing and development tooling:
pip install -r requirements/dev.txt
```

### 3. Frontend Installation
```powershell
cd d:\DoctorIn\frontend
npm install
```

---

## 🚀 Running DoctorIn (One Command)

### One-Click Quick Start (Windows)
Double-click:
```text
start-dev.bat
```
*(Or run `.\start-dev.ps1` in PowerShell)*

This automatically starts:
1. **FastAPI Backend** on `http://127.0.0.1:8000` with **automatic reload** on file changes.
2. **Next.js Frontend** on `http://localhost:3000` with **Hot Module Replacement (HMR)**.
3. Launches your default web browser to `http://localhost:3000`.

### Manual Startup (Two Terminals)

**Terminal 1 — Backend:**
```powershell
cd d:\DoctorIn\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```powershell
cd d:\DoctorIn\frontend
npm run dev
```

---

## 🔄 Automatic Refresh & Hot Reload

DoctorIn uses native framework development reloading:

* **Frontend (Next.js Fast Refresh)**:
  Any modification to React components, pages, or CSS in `frontend/src` is instantly hot-reloaded in the browser without losing component state.
* **Backend (Uvicorn `--reload`)**:
  Any modification to Python files in `backend/app` triggers an instant server restart in milliseconds without terminating the connection.

---

## ⚠️ Development vs. Production Mode

It is essential to understand the difference between local development and production hosting:

| Feature | Development Mode (`localhost`) | Production Mode (Cloud / AWS) |
| :--- | :--- | :--- |
| **Availability** | Available **ONLY** while your computer & terminal processes are running. | Available **24/7** independently across the internet. |
| **URL** | `http://localhost:3000` | Custom domain with HTTPS (e.g., `https://doctorin.com`). |
| **Hot Reload** | **Enabled** (updates instantly as you code). | **Disabled** (optimized, pre-compiled static bundles). |
| **Antigravity Dependency**| Stops if Antigravity / terminal is closed. | **Zero dependency** on your local machine or IDE. |
| **Database** | SQLite dev file (`doctorin_dev.db`) or local Docker. | Managed AWS RDS PostgreSQL with automated backups. |
| **Storage** | Local mock or MinIO bucket. | Private AWS S3 bucket with CloudFront CDN. |

---

## 🗄 Database Configuration

* **Local Development**: The project defaults to SQLite (`doctorin_dev.db`). The database tables and initial schema are automatically created on startup via `app.core.database.init_db`.
* **Production Database**: Point `DATABASE_URL` to a PostgreSQL instance. Alembic migrations manage schema evolutions:
  ```powershell
  cd backend
  alembic upgrade head
  ```

---

## 🧪 Running Tests

Run the complete test suite:
```powershell
.\scripts\test.bat
```

Or run individual suites:

**Backend Tests (pytest):**
```powershell
cd backend
python -m pytest tests -v
```

**Frontend Type Check:**
```powershell
cd frontend
npm run type-check
```

**Frontend Production Build Verification:**
```powershell
cd frontend
npm run build
```

---

## ☁️ Production Deployment Prerequisites

When ready to deploy DoctorIn to AWS:
1. **Container Hosting**: AWS App Runner or ECS Fargate using the multi-stage `Dockerfile` in `backend/` and `frontend/`.
2. **Database**: AWS RDS PostgreSQL (Multi-AZ recommended for high availability).
3. **Caching**: AWS ElastiCache for Redis (for distributed rate limiting and token management).
4. **Document Storage**: AWS S3 private bucket with IAM role access and presigned URL delivery.
5. **DNS & CDN**: AWS Route 53 and CloudFront for global caching and SSL/TLS termination.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
