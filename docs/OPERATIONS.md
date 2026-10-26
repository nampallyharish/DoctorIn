# DoctorIn — Production Operations & Maintenance Runbook

Welcome to the **DoctorIn** operational runbook. This guide contains instructions for running, operating, monitoring, and maintaining the platform in development and production environments.

---

## 1. System Architecture & Port Mapping

| Service | Technology | Port (Internal) | Host Port | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | Next.js 14 App Router + Tailwind | `3000` | `3000` | User portal, doctor discovery, messaging UI, admin |
| **Backend** | FastAPI + SQLAlchemy 2.0 Async | `8000` | `8000` | REST API, RBAC guardrails, OTP service, verification |
| **Database** | PostgreSQL 16 Alpine | `5432` | `5432` | Primary relational store (35+ tables) |
| **Cache / Queue** | Redis 7 Alpine | `6379` | `6379` | Token blacklist, sliding-window rate limiters, session state |
| **Reverse Proxy** | Nginx 1.25 Alpine | `80`, `443` | `80`, `443` | SSL termination, rate-limiting zones, static caching |

---

## 2. Quickstart & Local Execution

### Step 1: Start Database & Cache
```bash
# In project root (D:\DoctorIn)
docker compose up -d postgres redis
```

### Step 2: Initialize Database & Seed Specializations & Admin
```bash
cd backend
python -m scripts.init_db
```
*Creates initial specializations, cities, and root admin account (`admin@doctorin.app` / `DoctorInAdminPass2026!`).*

### Step 3: Run Backend Development Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
*API docs available at: `http://localhost:8000/docs`*

### Step 4: Run Frontend Development Server
```bash
cd frontend
npm run dev
```
*Web application available at: `http://localhost:3000`*

---

## 3. Production Deployment with Docker Compose

```bash
# 1. Copy production environment file
cp .env.production.example .env.production

# 2. Build and launch all production containers
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# 3. View live logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 4. Health Checks & Monitoring

### Liveness Probe
```bash
GET http://localhost:8000/api/v1/health
```

### Deep Infrastructure Diagnostics (PostgreSQL & Redis Latency)
```bash
GET http://localhost:8000/api/v1/health/deep
```
*Response sample:*
```json
{
  "status": "healthy",
  "timestamp": "2026-08-20T15:00:00Z",
  "components": {
    "postgresql": { "status": "connected", "latency_ms": 1.42 },
    "redis": { "status": "connected", "latency_ms": 0.58 }
  }
}
```

---

## 5. Automated Backups & Disaster Recovery

### Linux / Docker Host
```bash
bash backend/scripts/backup_db.sh
```

### Windows Host
```powershell
powershell -ExecutionPolicy Bypass -File backend\scripts\backup_db.ps1
```

### Database Restore Procedure
```bash
# Restore PostgreSQL from backup dump
gunzip -c /var/backups/doctorin/doctorin_backup_YYYYMMDD_HHMMSS.sql.gz | docker exec -i doctorin-postgres-prod psql -U doctorin_admin -d doctorin_db
```

---

## 6. Security Incident Response & Emergency Procedures

### Scenario A: Compromised Doctor Account
1. Log in to `/admin/users` as Administrator.
2. Search user by email or name.
3. Click **Suspend** or **Ban** — instantly revokes tokens and prevents active sessions.

### Scenario B: Revoke All Sessions for Specific User
Execute via API:
```bash
POST /api/v1/auth/logout-all
Authorization: Bearer <ADMIN_OR_USER_TOKEN>
```
*Immediately invalidates all refresh tokens and families for that account.*

---

## 7. Key Product Guardrails Recap

1. **Rule 1**: Patients cannot initiate direct doctor-to-doctor messages.
2. **Rule 2 & 3**: Only verified doctors can message other verified doctors.
3. **Rule 4**: Doctor verification is strictly admin-approved server-side (no self-verification).
4. **Rule 5**: Strict conversation membership validation on every API endpoint.
