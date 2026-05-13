# src/utils/drive_downloader.py
import os
import sys
import gdown

def download_from_gdrive(download_dir="documents"):
    """Download policy documents from Google Drive on startup."""
    folder_id = os.environ.get("GDRIVE_FOLDER_ID")
    if not folder_id:
        print("⚠️ GDRIVE_FOLDER_ID not set, skipping download", file=sys.stderr)
        return False

    os.makedirs(download_dir, exist_ok=True)

    # Skip if documents already downloaded (avoid re-downloading on warm restart)
    existing = [f for f in os.listdir(download_dir) if f.endswith(('.pdf', '.docx', '.txt'))]
    if existing:
        print(f"📁 Documents already present: {existing}", file=sys.stderr)
        return True

    print(f"⬇️ Downloading documents from Google Drive folder: {folder_id}", file=sys.stderr)
    try:
        gdown.download_folder(
            id=folder_id,
            output=download_dir,
            quiet=False,
            use_cookies=False
        )
        print("✅ Documents downloaded successfully", file=sys.stderr)
        return True
    except Exception as e:
        print(f"❌ Failed to download documents: {e}", file=sys.stderr)
        return False