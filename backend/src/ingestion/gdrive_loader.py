import os
import sys
import gdown

DOCUMENTS_DIR = "documents"

def download_from_gdrive():
    """Download policy documents from Google Drive on startup."""
    folder_id = os.environ.get("GDRIVE_FOLDER_ID")
    if not folder_id:
        print("⚠️ GDRIVE_FOLDER_ID not set, skipping download", file=sys.stderr)
        return

    os.makedirs(DOCUMENTS_DIR, exist_ok=True)

    # Skip if documents already downloaded (avoid re-downloading on warm restart)
    existing = [f for f in os.listdir(DOCUMENTS_DIR) if f.endswith(('.pdf', '.docx'))]
    if existing:
        print(f"📁 Documents already present: {existing}", file=sys.stderr)
        return

    print(f"⬇️ Downloading documents from Google Drive folder: {folder_id}", file=sys.stderr)
    try:
        gdown.download_folder(
            id=folder_id,
            output=DOCUMENTS_DIR,
            quiet=False,
            use_cookies=False
        )
        print("✅ Documents downloaded successfully", file=sys.stderr)
    except Exception as e:
        print(f"❌ Failed to download documents: {e}", file=sys.stderr)
        raise