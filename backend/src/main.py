from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Any, Optional
import uvicorn

# Correct import - process_email is now available
from src.agent.email_agent import process_email
from src.ingestion import run_ingestion
from src.models import EmailInput, EmailResponse, IngestResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Email Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",                    # Local development
        "https://*.streamlit.app",                   # All Streamlit Cloud apps
        "https://your-frontend-name.streamlit.app",  # Your specific app (update later)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Email Assistant API is active."}

@app.post("/ingest", response_model=IngestResponse)
def trigger_ingestion(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(run_ingestion)
        return IngestResponse(
            status="started",
            documents_processed=0,
            chunks_created=0,
            message="Ingestion started in background."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-email", response_model=EmailResponse)
async def process_email_endpoint(email: EmailInput):
    try:
        # Input validation
        if not email.body or not email.body.strip():
            raise HTTPException(
                status_code=400,
                detail="Email body cannot be empty."
            )

        # Format the full email content
        full_content = f"Subject: {email.subject}\nFrom: {email.sender}\n\n{email.body}"

        # Process the email
        response = process_email(full_content)
        
        return response

    except Exception as e:
        error_str = str(e).lower()
        # Check if it's a quota error
        if "quota_exceeded" in error_str or ("429" in error_str and "quota" in error_str):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "quota_exceeded",
                    "message": "Daily API quota exceeded. Please try again tomorrow.",
                    "limit": 20,
                    "model": "gemini-2.5-flash"
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing email: {str(e)}"
            )
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )