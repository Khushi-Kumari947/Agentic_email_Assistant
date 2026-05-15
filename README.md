# AI Email Assistant

An AI-powered email response assistant for employee inquiries. The application reads company policy documents, indexes them in Pinecone, and uses a LangChain agent with Google Gemini to generate professional email replies with confidence scoring, category classification, and human-review flags.

---

# Live Demo

## Frontend Application
https://agentic-email-assistant.streamlit.app/

## Backend API
https://agentic-email-assistant-2.onrender.com

## API Documentation
https://agentic-email-assistant-2.onrender.com/docs

---

# Features

- Process employee email queries through a FastAPI backend
- Generate professional email draft replies using Google Gemini
- Perform retrieval-augmented generation (RAG) over company policies
- Store and query embeddings using Pinecone
- Ingest policy documents directly from Google Drive
- Classify responses into:
  - Policy queries
  - General inquiries
  - Sensitive matters
  - Clarification requests
- Flag sensitive or low-confidence responses for human review
- Streamlit frontend with:
  - Compose email interface
  - Response history
  - Backend connection status

---

# Tech Stack

| Area | Technology |
|---|---|
| Backend API | FastAPI, Uvicorn, Pydantic |
| AI Agent | LangChain ReAct Agent |
| LLM | Google Gemini 2.5 Flash |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Database | Pinecone |
| Document Parsing | pypdf, python-docx, TXT |
| Frontend | Streamlit |
| File Source | Google Drive via gdown |

---

# Project Structure

```text
Email_Assistant_Agent/
│
├── backend/
│   ├── Dockerfile
│   ├── render.yaml
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       ├── models.py
│       ├── config.py
│       │
│       ├── agent/
│       │   ├── email_agent.py
│       │   └── tools.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── document_loader.py
│       │   └── vector_store.py
│       │
│       └── utils/
│           └── drive_downloader.py
│
├── frontend/
│   ├── frontend.py
│   ├── config.py
│   └── requirements.txt
│
└── README.md
```

---

# Prerequisites

- Python 3.11 or above
- Google Gemini API Key
- Pinecone API Key
- Pinecone Index
- Google Drive folder containing policy documents

> The embedding model `sentence-transformers/all-MiniLM-L6-v2` generates **384-dimensional embeddings**. Ensure your Pinecone index is configured with the same dimension.

---

# Environment Variables

Create a `.env` file inside the `backend/` directory.

## Backend

```env
GOOGLE_API_KEY=your_google_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=email-assistant
GDRIVE_FOLDER_ID=your_google_drive_folder_id
```

## Frontend

```env
API_BASE_URL=https://agentic-email-assistant-2.onrender.com
```

---

# Backend Setup

```bash
cd backend

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn src.main:app --reload
```

## Backend URLs(Localhost)

| Service | URL |
|---|---|
| API Root | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

# Frontend Setup

Open a second terminal:

```bash
cd frontend

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

streamlit run frontend.py
```

The Streamlit frontend will typically run at:

```text
http://localhost:8501
```

---

# Document Ingestion

1. Upload supported policy files to the configured Google Drive folder
2. Ensure the backend environment variables are configured correctly
3. Start the backend server
4. Trigger ingestion

## Ingestion Request

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/ingest
```

---

# Supported File Formats

- PDF
- DOCX
- TXT

---

# Ingestion Workflow

The ingestion pipeline:

1. Downloads files from Google Drive
2. Stores them in a local `documents/` folder
3. Extracts text from files
4. Splits content into chunks
5. Generates embeddings
6. Uploads vectors to Pinecone

---

# API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/ingest` | Start document ingestion |
| POST | `/process-email` | Generate email response |

---

# Process Email Example

## Request

```json
{
  "subject": "Sick leave policy",
  "body": "How many sick days do I get?",
  "sender": "employee@company.com",
  "recipient": "hr@company.com"
}
```

## Response

```json
{
  "draft_reply": "Subject: Re: Sick leave policy\n\nDear Employee,\n\n...",
  "category": "policy_query",
  "retrieved_docs": [],
  "confidence_score": 0.85,
  "requires_human_review": false,
  "clarification_needed": false,
  "clarification_question": null
}
```

---

# Deployment Notes

The backend includes:

- `Dockerfile`
- `render.yaml`

Configure the following environment variables in your deployment platform:

```env
GOOGLE_API_KEY
PINECONE_API_KEY
PINECONE_INDEX_NAME
GDRIVE_FOLDER_ID
```

For Streamlit Cloud deployments:

```env
API_BASE_URL=https://agentic-email-assistant-2.onrender.com
```

---

# Troubleshooting

## Frontend Shows "Disconnected"

- Ensure the backend server is running
- Verify `API_BASE_URL` points to the correct backend URL

## No Documents Found During Ingestion

- Verify `GDRIVE_FOLDER_ID`
- Check Google Drive folder permissions

## Pinecone Query Errors

Ensure:

- Pinecone API key is valid
- Index name is correct
- Embedding dimensions match

## Gemini Quota Errors

If Gemini quota limits are exceeded:

- The application surfaces a quota warning
- The response is automatically flagged for human review

---

# Future Improvements

- Multi-language email support
- User authentication and role-based access
- Email sending integration
- Conversation memory for follow-up emails
- Admin dashboard for monitoring queries
- Analytics and reporting system
- Hybrid search support
- Better confidence evaluation pipeline

---

