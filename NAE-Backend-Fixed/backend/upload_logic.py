import os
import time
import random
from datetime import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIG ===
CREDENTIALS_PATH = r"C:\Development\myenv\Scripts\Google App\python_api.json"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPE)
CLIENT = gspread.authorize(CREDS)

SHEET_ID = "1_GpYih_KpE4N0OpmY231780v9aga5DaqtLh68xoX6KE"
SHEET_NAME = "Asset Management Monitoring"
LOG_PATH = "log.txt"

DIAGNOSTIC_MAP = {
    "IZWI Fault": "Faulty",
    "EPS Fault": "Faulty",
    "Bin Tips Fault": "Faulty",
    "Brake Test Not Compliant": "Faulty"
}

def log_event(filename, sheet, status, attempt):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {filename} | {sheet} | {status} | {attempt}\n")

def validate_filename(filename, expected_keyword):
    return expected_keyword.lower() in filename.lower()

def sort_sheet(sheet):
    try:
        sheet.sort((1, 'asc'))
        time.sleep(1)  # slow down sorting too
    except Exception as e:
        log_event("SYSTEM", SHEET_NAME, f"Sort Error: {e}", 0)

def update_cell_with_retry(ws, row, col, value, retries=3):
    for attempt in range(retries):
        try:
            ws.update_cell(row, col, value)
            time.sleep(1)
            return
        except Exception as e:
            if "429" in str(e):
                wait = (2 ** attempt) + random.uniform(0.5, 1.5)
                print(f"⚠️  Quota hit. Retrying row {row}, col {col} in {wait:.2f}s...")
                time.sleep(wait)
            else:
                raise

def update_status_based_on_events(ws):
    data = ws.get_all_records()
    for idx, row in enumerate(data, start=2):
        if row.get('Events'):
            new_status = DIAGNOSTIC_MAP.get(row['Events'], 'Working')
            try:
                update_cell_with_retry(ws, idx, 4, new_status)
            except Exception as e:
                log_event("SYSTEM", SHEET_NAME, f"Status update error: {e}", 0)

def process_upload_file(file_type, file_path):
    filename = os.path.basename(file_path)
    
    if file_type == "asset" and not validate_filename(filename, "asset export"):
        print("❌ Skipped (Filename does not match Asset Export)")
        return False
    elif file_type == "event" and not validate_filename(filename, "event listing"):
        print("❌ Skipped (Filename does not match Event Listing)")
        return False
    elif file_type == "lastseen" and not validate_filename(filename, "last seen"):
        print("❌ Skipped (Filename does not match Last Seen)")
        return False

    try:
        df = pd.read_excel(file_path)
        sheet = CLIENT.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        existing_data = sheet.get_all_records()

        for _, row in df.iterrows():
            asset = str(row.get("Asset", "")).strip()
            site = str(row.get("Site", "")).strip()
            asset_type = str(row.get("Type", "")).strip()
            event = str(row.get("Event", "")).strip()

            if not asset and not site and not asset_type:
                continue
            if asset and (not site or not asset_type):
                continue

            matched_row = None
            for idx, existing_row in enumerate(existing_data, start=2):
                if existing_row.get("Asset") == asset and existing_row.get("Mine") == site:
                    matched_row = idx
                    break

            if matched_row:
                try:
                    update_cell_with_retry(sheet, matched_row, 5, event)  # E
                    diagnosis = DIAGNOSTIC_MAP.get(event, "Working")
                    update_cell_with_retry(sheet, matched_row, 6, diagnosis)  # F
                    update_cell_with_retry(sheet, matched_row, 7, 1)  # G
                except Exception as e:
                    log_event(filename, SHEET_NAME, f"Update Error: {e}", 1)
            else:
                log_event(filename, SHEET_NAME, "No Asset Match", 0)

        update_status_based_on_events(sheet)
        sort_sheet(sheet)
        log_event(filename, SHEET_NAME, "Uploaded", 1)
        print("✅ Upload completed")
        return True

    except Exception as e:
        log_event(filename, SHEET_NAME, f"Error: {e}", 1)
        print("❌ Upload failed:", e)
        return False


if __name__ == "__main__":
    print("🔁 Auto-sync started: syncing every 15 minutes.")
    while True:
        try:
            # Replace this with your main upload function
            # Example: process_all_diagnostics()
            print("⏳ Running sync task...")
            # Simulated function call (adjust as needed)
            # process_all_diagnostics()

            # Log to terminal
            print("✅ Sync complete. Sleeping for 15 minutes...")
        except Exception as e:
            print(f"❌ Error during sync: {e}")

        time.sleep(900)  # 15 minutes
