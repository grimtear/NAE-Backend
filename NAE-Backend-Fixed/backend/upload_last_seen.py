import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_ID = "1_GpYih_KpE4N0OpmY231780v9aga5DaqtLh68xoX6KE"
SHEET_NAME = "Last Seen"

def upload_last_seen(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    sheet_data = sheet.get_all_values()
    headers, rows = sheet_data[0], sheet_data[1:]
    df_sheet = pd.DataFrame(rows, columns=headers)

    for idx, row in df_sheet.iterrows():
        if row["Asset"] in df["Asset"].values:
            sheet.update_cell(idx + 2, 9, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # I
