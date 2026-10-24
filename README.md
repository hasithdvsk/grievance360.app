# 🏛️ Grievance360° | AICTE Autonomous AI-Powered Grievance Redressal Platform

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fhasithdvsk%2FGrievance360&root-directory=apps%2Fweb)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://dashboard.render.com/blueprint/new)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2-black?style=flat&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostGIS-WGS84-336791?style=flat&logo=postgresql)](https://postgis.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-white.svg)](https://opensource.org/licenses/MIT)

**Grievance360°** is an enterprise AI-powered statutory grievance redressal ecosystem engineered for AICTE educational institutions across India. It unifies real-time SentenceTransformers NLP semantic routing, multi-modal statutory documentary/video evidence verification, OpenAI Whisper multilingual voice ingestion, PostGIS WGS 84 geospatial hotspot clustering, and automated ReportLab Action Taken Report (ATR) PDF generation.

---

## 🌟 Key Features

### 1. 🛡️ Multi-Modal Stronger Evidence Verification Vault
- **Documents to Verify**: Direct ingestion of PDFs, Word documents, affidavits, circulars, fee receipts, and medical certificates.
- **Photos for Stronger Evidence**: Incident photography, hostel roll call notices, WhatsApp/email intimidation screenshots, and physical infrastructure damage proofs with real-time thumbnail previews.
- **Video & Audio Proof**: CCTV footage, mobile video recordings, and voice memos supporting priority statutory investigation.
- **Dynamic Confidence Scoring**: Automated calculation of evidence strength (`STANDARD`, `HIGH`, `MAXIMUM STATUTORY EVIDENCE`) that accelerates bureau resolution SLA targets by up to 70%.

### 2. 🎙️ OpenAI Whisper Multilingual Voice Ingestion
- Real-time speech-to-text supporting Indian languages (Hindi, Tamil, Telugu, Marathi, Bengali, and English).
- Automatic English translation synthesis formatted for official ombudsman review and NLP embedding parsing.

### 3. 🧠 SentenceTransformers NLP Triage Engine
- Autonomous bureau jurisdiction classification (`Anti-Ragging`, `Approval & Intake`, `Finance & Scholarships`, `Legal & Disciplinary`, `General Administration`).
- Critical keyword tripwire detector (`suicide`, `ragging`, `threat`, `violence`, `bribe`) that triggers expedited `<12h` emergency SLA routing and nodal officer dispatch.

### 4. 🗺️ PostGIS Geospatial Hotspots & Regional Analytics
- Monochromatic, high-contrast analytics dashboard tracking educational institutions clustered via WGS 84 (`GEOGRAPHY(POINT, 4326)`) coordinates and spatial GIST indexes.
- Highlighted clean metric typography for Compliance Rating, Total Intake, Unresolved Cases, and Critical Incidents without cluttering boxes or badge borders.

### 5. 📑 ReportLab Action Taken Report (ATR) Exporter
- On-demand statutory ATR PDF generation with cryptographic SHA-256 verification seals, chronological investigation audit ledgers, and institutional compliance rankings.

### 6. ✨ GSAP & Awwwards-Inspired Ambient Kinetic Background
- Ultra-fluid, non-dominating particle constellation with organic Brownian drift and proximity filaments.
- Monochromatic luminescent auroras with subtle breathing keyframes and a technical grid horizon.
- Zero layout shift and GPU-accelerated 60 FPS rendering with automatic tab-inactivity battery saver.

### 7. 📱 100% Responsive Adaptive Layout
- Pixel-perfect screen ratio adaptation from mobile phones (360px–480px), tablets (768px–1024px), laptops (1280px–1536px), up to ultra-wide displays.
- Balanced grid column reflows, mobile horizontal table scrolling with frozen headers, and touch-optimized action targets.

---

## 🗂️ Monorepo Architecture

```
Grievance360/
├── apps/
│   ├── web/                    # Next.js 14 App Router Frontend
│   │   ├── app/                # Next.js App Router (Home, File Complaint, Admin Dashboard)
│   │   ├── components/         # Reusable UI & Animation components
│   │   │   ├── animations/     # AmbientBackground, ScrambleText, SplitText, Preloader
│   │   │   ├── ComplaintTracker.tsx
│   │   │   ├── VoiceRecorder.tsx
│   │   │   └── Navbar.tsx
│   │   └── package.json
│   └── api/                    # FastAPI Python 3.11 Backend
│       ├── routers/            # Complaints, Analytics, Multilingual, WhatsApp, Telegram
│       ├── services/           # SentenceTransformers NLP Engine, ATR Generator
│       ├── schemas/            # Pydantic v2 validation models
│       ├── main.py             # FastAPI entrypoint
│       └── requirements.txt
├── packages/
│   └── db/                     # PostgreSQL Schema, PostGIS DDL, and Seeding Scripts
├── render.yaml                 # Infrastructure-as-Code Blueprint for Render Fullstack Deploy
├── vercel.json                 # Monorepo configuration for Vercel Cloud Deploy
└── docker-compose.yml          # Local container orchestration
```

---

## 🚀 One-Click Cloud Deployments

### 1. Deploying Frontend to Vercel
Deploy the Next.js web application with native Server Components, Edge Caching, and zero-configuration monorepo pipelines:

1. Click the button below:  
   [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fhasithdvsk%2FGrievance360&root-directory=apps%2Fweb)
2. Connect your GitHub account and select your `Grievance360` repository.
3. Keep the pre-configured root directory (`apps/web` or root) and click **Deploy**.
4. Set optional environment variable:
   - `NEXT_PUBLIC_API_URL`: Your deployed FastAPI backend URL (e.g. `https://grievance360-api.onrender.com`).

---

### 2. Deploying Fullstack to Render
Deploy the FastAPI backend, PostgreSQL 15 database, Redis cache, and Next.js frontend using the included [`render.yaml`](./render.yaml) blueprint:

1. Click the button below:  
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://dashboard.render.com/blueprint/new)
2. Connect your repository `https://github.com/hasithdvsk/Grievance360`.
3. Click **Apply Blueprint**. Render automatically provisions:
   - `grievance360-api`: FastAPI Python Web Service with SentenceTransformers.
   - `grievance360-web`: Next.js Web App with automatic `$PORT` binding.
   - `grievance360-db`: Managed PostgreSQL database with PostGIS extensions.
   - `grievance360-redis`: Redis instance for async tasks and caching.

---

## 🛠️ Local Development & Quick Start

### 1. Prerequisites
- **Node.js**: v18.17+ or v20.x LTS
- **Python**: 3.11+
- **Docker & Docker Compose**: (Optional, for full containerized stack)

### 2. Running Locally

#### Start the Next.js Frontend (`apps/web`):
```bash
# From repository root:
npm install
npm run dev:web
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

#### Start the FastAPI Backend (`apps/api`):
```bash
cd apps/api
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API Documentation available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/healthz](http://localhost:8000/healthz)

---

## 📦 Technology Stack

| Layer | Technologies | Role in System |
| :--- | :--- | :--- |
| **Frontend Web** | Next.js 14, React 18, TypeScript, Tailwind CSS | App Router, Server Components, Monochromatic Noir Theme |
| **Animation & Motion** | Framer Motion, HTML5 Canvas, GSAP Kinetic Engine | Non-dominating ambient background, scramble typography, page transitions |
| **Backend API** | FastAPI, Python 3.11, Uvicorn, Pydantic v2 | High-concurrency async endpoints, auto OpenAPI schemas |
| **Machine Learning** | PyTorch, SentenceTransformers (`all-MiniLM-L6-v2`), Whisper | Semantic bureau routing, duplicate detection, voice transcription |
| **Data & Spatial** | PostgreSQL 15, PostGIS (`GEOGRAPHY(POINT, 4326)`), GIST Indexes | Geospatial clustering, regional hotspot tracking |
| **Document Engine** | ReportLab 4.1, SHA-256 Checksums | Digitally verifiable Action Taken Report PDF ledger generation |
| **Cloud DevOps** | Vercel, Render Blueprints, Docker Compose | Zero-config production deployment and multi-stage container builds |

---

## 📄 License
This project is licensed under the MIT License — AICTE Grievance360 Core Engineering Team.
