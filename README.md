# 🤖 AI Email Assistant

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.1%2B-orange)](https://langchain.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5-yellow)](https://deepmind.google/technologies/gemini/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-red)](https://streamlit.io)
[![ngrok](https://img.shields.io/badge/ngrok-Tunnel-blueviolet)](https://ngrok.com)

An intelligent email assistant that automatically understands and responds to employee inquiries by leveraging company policy documents through **RAG** and **agent-based architecture**.

---

## ✨ Features

- **📧 Smart Email Processing**: Automatically analyzes intent and generates context-aware replies
- **📚 RAG-Based Retrieval**: Searches company policies using semantic similarity for accurate responses
- **🤖 Agent Reasoning**: Decides when to search policies, escalate to humans, or ask for clarification
- **🔍 Semantic Search**: FAISS vector store with sentence transformers for fast document retrieval
- **🏷️ Smart Categorization**: Classifies emails as policy queries, sensitive matters, or general inquiries
- **⚠️ Intelligent Escalation**: Automatically flags sensitive matters for human review

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, LangChain, Google Gemini 2.5 |
| **Vector DB** | FAISS with Sentence Transformers |
| **Frontend** | Streamlit |
| **Tunneling** | ngrok (for exposing local backend) |
| **Frontend Hosting** | Streamlit Cloud |

---

## 🏗️ Architecture

```
Employee Query → Streamlit Cloud → ngrok Tunnel → Local Backend → LangChain Agent → Policy Search (FAISS) → Gemini LLM → Professional Reply
                                    ↓                            ↓
                              Human Escalation              Email Response
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Gemini API key ([Get one](https://makersuite.google.com/app/apikey))
- ngrok account (free) for tunneling ([Sign up](https://dashboard.ngrok.com/signup))

### Local Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ai-email-assistant.git
cd ai-email-assistant

# Backend setup
cd backend
cp .env.example .env        # Add your Gemini API key
pip install -r requirements.txt
uvicorn src.main:app --reload

# Expose backend with ngrok (new terminal)
ngrok http 8000
# Copy the https URL (e.g., https://your-tunnel.ngrok-free.dev)

# Frontend setup (new terminal)
cd frontend
pip install -r requirements.txt
streamlit run frontend.py
```

Access:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000/docs
- Public API URL: Your ngrok URL

---

## 📁 Project Structure

```
ai-email-assistant/
├── backend/                 # FastAPI app
│   ├── src/
│   │   ├── agent/          # LangChain agent logic
│   │   ├── ingestion/      # RAG pipeline
│   │   ├── main.py         # API endpoints
│   │   └── config.py       # Configuration
│   ├── documents/          # Policy files (add your PDFs here)
│   └── requirements.txt
├── frontend/                # Streamlit app
│   ├── frontend.py
│   └── requirements.txt    # streamlit, requests only
└── README.md
```

---

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/process-email` | Process email and generate reply |
| `POST` | `/ingest` | (Admin) Update FAISS from documents |
| `GET` | `/health` | Health check |
| `GET` | `/stats` | System statistics |

### Example Request

```json
POST /process-email
{
  "subject": "Sick leave policy",
  "body": "How many sick days do I get?",
  "sender": "employee@company.com"
}
```

### Example Response

```json
{
  "draft_reply": "Subject: Re: Sick leave policy\n\nDear Employee,\n\nYou get 12 paid sick days per year...\n\nBest regards,\nHR Department",
  "category": "policy_query",
  "confidence_score": 0.94
}
```

---

## 🧪 Sample Tests

### Test Emails for Different Scenarios

| Scenario | Sample Input |
|----------|--------------|
| **Policy Query** | `{"subject": "Sick leave policy", "body": "How many sick days do I get?", "sender": "employee@company.com"}` |
| **Work From Home** | `{"subject": "Remote work", "body": "Can I work from home on Fridays?", "sender": "employee@company.com"}` |
| **Sensitive Matter** | `{"subject": "Harassment complaint", "body": "I need to report inappropriate behavior", "sender": "employee@company.com"}` |
| **Benefits Question** | `{"subject": "Health insurance", "body": "Does dental cover root canals?", "sender": "employee@company.com"}` |
| **Vacation Request** | `{"subject": "Vacation", "body": "How do I request time off?", "sender": "employee@company.com"}` |

### Quick Test Script

```python
import requests

API_URL = "https://your-tunnel.ngrok-free.dev/process-email"

test_email = {
    "subject": "Sick leave policy",
    "body": "How many sick days do I get?",
    "sender": "test@company.com"
}

response = requests.post(API_URL, json=test_email)
print(response.json())
```

---

## 🌐 Live Demo

- **Frontend (Streamlit Cloud)**: [https://ai-email-assistant.streamlit.app](https://agentic-email-assistant.streamlit.app/)
- **Backend API (via ngrok)**: [https://your-tunnel.ngrok-free.dev/docs](https://leana-unsick-mira.ngrok-free.dev) (Contact for current URL if this doesn't work as it changes on restart)

---

## 🚢 Deployment

### Backend: Local + ngrok Tunnel

Due to **Railway free trial expiration** and limited free tier options for ML-focused backends, the backend is currently hosted locally and exposed via **ngrok**:

```bash
# Start backend locally
cd backend
uvicorn src.main:app --reload

# Expose with ngrok
ngrok http 8000
# Public URL: https://your-tunnel.ngrok-free.dev
```

**Note**: 
- The ngrok URL changes each time the tunnel is restarted
- Backend runs on local machine (requires internet and uptime)
- Perfect for demonstration and development purposes

### Frontend: Streamlit Cloud

The frontend is deployed on **Streamlit Cloud** (free tier):

```bash
1. Go to share.streamlit.io
2. Connect GitHub repository
3. Set main file: frontend/frontend.py
4. Add environment secret:
   - Key: `API_BASE_URL`
   - Value: Current ngrok URL (e.g., `https://your-tunnel.ngrok-free.dev`)
5. Deploy! 🚀
```

**Why this setup?**
- ✅ Railway free trial expired
- ✅ Render free tier has limitations for ML apps
- ✅ Streamlit Cloud offers generous free tier for frontend
- ✅ ngrok provides easy tunneling for local backend
- ✅ Cost-effective for demonstration
  
---

## 🔮 Future Roadmap

- [ ] **Slack/Teams integration** for instant messaging
- [ ] **Email auto-responder** with IMAP integration
- [ ] **Analytics dashboard** with usage metrics
- [ ] **Multi-language support** for global teams
- [ ] **Cloud deployment** when budget permits

---

## ⚠️ Important Notes

- The backend runs locally, so it's only available when your machine is on
- ngrok URL changes on restart - update Streamlit secrets accordingly
- Free ngrok has limitations: 40 connections/minute, 4 tunnels/process
- For production use, consider deploying on a cloud platform with persistent storage

---

**⭐ If you find this useful, please star the repo!**
