from fastapi import FastAPI, HTTPException, BackgroundTasks
import uvicorn
import os
# Correct import - process_email is now available
from src.agent.email_agent import process_email
from src.ingestion import run_ingestion
from src.models import EmailInput, EmailResponse, IngestResponse
from fastapi.middleware.cors import CORSMiddleware

# At the top of src/main.py
import sys
import traceback

print("=" * 50, file=sys.stderr)
print("STARTING FULL APPLICATION", file=sys.stderr)
print("=" * 50, file=sys.stderr)

try:
    print("1. Importing config...", file=sys.stderr)
    from src import config
    print(f"   - GOOGLE_API_KEY set: {bool(config.GOOGLE_API_KEY)}", file=sys.stderr)
except Exception as e:
    print(f"❌ Config import failed: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

try:
    print("2. Importing models...", file=sys.stderr)
    from src import models
    print("   - Models imported successfully", file=sys.stderr)
except Exception as e:
    print(f"❌ Models import failed: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

try:
    print("3. Importing ingestion module...", file=sys.stderr)
    from src import ingestion
    print("   - Ingestion imported successfully", file=sys.stderr)
except Exception as e:
    print(f"❌ Ingestion import failed: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

try:
    print("4. Importing email agent...", file=sys.stderr)
    from src.agent import email_agent
    print("   - Email agent imported successfully", file=sys.stderr)
except Exception as e:
    print(f"❌ Email agent import failed: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

print("=" * 50, file=sys.stderr)
print("ALL IMPORTS SUCCESSFUL", file=sys.stderr)
print("=" * 50, file=sys.stderr)

# actual code before
app = FastAPI(title="AI Email Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
    ],
    allow_origin_regex=r"https://.*\.streamlit\.app",
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
@app.api_route("/", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}

@app.get("/health")
def health_check():
    return {"healthy": True}