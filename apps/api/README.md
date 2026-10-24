# ⚙️ Grievance360 API Service

FastAPI-powered RESTful and asynchronous backend for intelligent grievance redressing, semantic text analysis, real-time ticket triage, and automated reporting.

---

## 📦 Installed Packages & Stack

- **fastapi**: High performance asynchronous web framework
- **uvicorn**: Lightning-fast ASGI web server
- **pydantic**: Data validation and settings management using Python type annotations
- **sentence-transformers & torch**: NLP embeddings for semantic similarity, duplicate detection, and category classification
- **psycopg2-binary**: PostgreSQL database adapter
- **redis**: In-memory caching and Celery message broker
- **celery**: Asynchronous distributed task queue for heavy NLP tasks & PDF generation
- **reportlab**: PDF grievance resolution letter and status report generator
- **numpy**: High performance vector operations and similarity calculations
- **python-dotenv**: Environment configuration loading

---

## 🛠️ Setup & Running

### 1. Create Virtual Environment
```bash
python -m venv .venv
```

### 2. Activate Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Windows (CMD)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Server
```bash
uvicorn main:app --reload --port 8000
```

- API Base: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- ReDoc Docs: `http://localhost:8000/redoc`
