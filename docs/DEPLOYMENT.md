# Grievance360 Cloud Deployment & Production CI/CD Guide

This guide details the automated, zero-downtime production deployment of **Grievance360** using **Vercel** for the Next.js frontend and **Render** for the FastAPI backend, PostgreSQL (with PostGIS), and Redis.

```
┌─────────────────────────────────┐        API Rewrites        ┌───────────────────────────────────┐
│         Vercel Cloud            │ ─────────────────────────> │           Render Cloud            │
│  Next.js 14 Standalone Frontend │ <───────────────────────── │ FastAPI + SentenceTransformers    │
│    (Mobile-Optimized Glass UI)  │   CORS: *.vercel.app       │         (Python 3.11)             │
└─────────────────────────────────┘                            └─────────────────┬─────────────────┘
                                                                                 │
                                                        ┌────────────────────────┴───────────────────────┐
                                                        │                                               │
                                             ┌──────────▼───────────┐                       ┌───────────▼──────────┐
                                             │  Render PostgreSQL   │                       │     Render Redis     │
                                             │   (PostGIS Spatial)  │                       │   (SLA Watchtower)   │
                                             └──────────────────────┘                       └──────────────────────┘
```

---

## 🚀 3-Step Automated Cloud Deployment

### Step 1: Push Codebase to GitHub
Ensure all latest files and configuration blueprints are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "feat(deploy): configure automated deployment for Vercel and Render"
git push origin main
```
*Repository URL:* `https://github.com/hasithdvsk/Grievance360`

---

### Step 2: Deploy Backend & Database on Render (Infrastructure as Code)
Render automatically provisions the FastAPI service, PostgreSQL database, and Redis cache using the [`render.yaml`](../render.yaml) blueprint in the repository root.

1. Navigate to [Render Blueprints](https://dashboard.render.com/blueprints).
2. Click **New Blueprint Instance**.
3. Connect your GitHub account and select the **`Grievance360`** repository.
4. Render will parse `render.yaml` and display the resources to create:
   - **`grievance360-api`** (Python Web Service)
   - **`grievance360-db`** (PostgreSQL 15 Database)
   - **`grievance360-redis`** (Key-Value Redis Store)
5. Click **Apply**.
6. Once deployed, note your public Render API URL:
   `https://grievance360-api.onrender.com`
7. Verify backend healthcheck:
   ```bash
   curl -I https://grievance360-api.onrender.com/healthz
   # Should return HTTP 200 OK: {"status": "healthy"}
   ```

---

### Step 3: Deploy Frontend on Vercel
Vercel hosts the Next.js 14 App Router frontend with global edge caching and instant mobile responsiveness.

1. Navigate to [Vercel New Project](https://vercel.com/new).
2. Select your **`Grievance360`** GitHub repository.
3. Configure the **Root Directory**:
   - Set **Root Directory** to: `apps/web`
4. Configure **Environment Variables**:
   | Variable Name | Value | Purpose |
   | :--- | :--- | :--- |
   | `NEXT_PUBLIC_API_URL` | `https://grievance360-api.onrender.com` | Target Render FastAPI backend |
5. Click **Deploy**.
6. Vercel will build the standalone Next.js bundle and provide your production URL:
   `https://grievance360.vercel.app` (or your assigned Vercel URL)

---

## 🔄 Automated CI/CD (Continuous Deployment)
Both platforms listen to the `main` branch:
- Any `git push origin main` triggers an automatic build on Vercel and Render.
- **Render Zero-Downtime**: Old instances continue serving traffic until new FastAPI containers pass the `/healthz` check.
- **Vercel Instant Rollback**: Atomic deployments ensure zero partial-loading states.

---

## 📱 Cross-Device Optimization & Fallback Guarantees
- **Mobile First**: All pages (`/`, `/file-complaint`, `/admin/dashboard`) include fluid viewport breakpoints (`sm:`, `md:`, `lg:`) and touch-friendly controls.
- **Low-Bandwidth Resiliency**: If the cloud API experiences cold starts, the frontend displays skeleton loaders (`Loader2`) and seamlessly activates built-in mock fallback records so users can interact without lag.
- **Dynamic Rewrites**: Configured in `apps/web/next.config.js` to route `/api/v1/*` requests directly through Next.js proxy rewrite layers.

---

## 🛠️ Verification Checklist

- [x] Lightweight health probe: `GET /healthz`
- [x] Full service probe: `GET /api/v1/health/`
- [x] Interactive API Documentation: `GET /docs` and `GET /redoc`
- [x] In-App AI Chatbot: `POST /api/v1/bot/chat`
- [x] Twilio WhatsApp Webhook: `POST /api/v1/bot/whatsapp`
- [x] Telegram Webhook: `POST /api/v1/bot/telegram`
- [x] Multilingual Voice Transcription: `POST /api/v1/multilingual/submit-voice`
