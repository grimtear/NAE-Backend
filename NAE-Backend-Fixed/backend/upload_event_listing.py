import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

DIAGNOSTIC_MAP_EVENT_LISTING = {
    "IZWI Fault": "IZWI Communication Error",
    "EPS Fault": "Electrical Power System Fault",
    "Bin Tips Fault": "Unstable Tipping Sensor",
    "Brake Test Not Compliant": "Brake Check Failed",
}

RED_FLAGS = [
    ("NFMS not updating", None),
    ("NFMS not working", None),
    ("Supply High Voltage", 3),
    ("Ignition Off While Driving", 4),
    ("Power Disconnect", 4),
    ("Internal Battery Faulty", 4),
    ("Unknown Driver", 3),
]

SHEET_ID = "1_GpYih_KpE4N0OpmY231780v9aga5DaqtLh68xoX6KE"
SHEET_NAME = "Event Listing"

def is_red_flag(event, count):
    for flag, threshold in RED_FLAGS:
        if flag in event:
            if threshold is None or count >= threshold:
                return True
    return False

def upload_event_listing(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    sheet_data = sheet.get_all_values()
    headers, rows = sheet_data[0], sheet_data[1:]
    df_sheet = pd.DataFrame(rows, columns=headers)

    grouped = df.groupby(["Asset", "Event"]).size().reset_index(name="Count")

    for _, row in grouped.iterrows():
        asset, event, count = row["Asset"], row["Event"], row["Count"]
        diagnosis = DIAGNOSTIC_MAP_EVENT_LISTING.get(event, "Unknown Issue")
        is_red = is_red_flag(event, count)
        new_status = "Faulty" if is_red else "Working"

        for idx, sheet_row in df_sheet.iterrows():
            if sheet_row["Asset"] == asset:
                sheet.update_cell(idx + 2, 4, new_status)      # D
                sheet.update_cell(idx + 2, 5, event)           # E
                sheet.update_cell(idx + 2, 6, diagnosis)       # F
                sheet.update_cell(idx + 2, 7, count)           # G
                sheet.update_cell(idx + 2, 10, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # J
                break
