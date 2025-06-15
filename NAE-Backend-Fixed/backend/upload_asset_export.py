import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_ID = "1_GpYih_KpE4N0OpmY231780v9aga5DaqtLh68xoX6KE"
TARGET_SHEET_NAME = "Asset Export"

def upload_asset_export(excel_path):
    df = pd.read_excel(excel_path, header=None)

    site_name = str(df.iloc[0, 0]).strip()
    asset_types = df.iloc[2:, 0].astype(str).str.strip().tolist()
    asset_names = df.iloc[2:, 2].astype(str).str.strip().tolist()

    if not site_name or not asset_names:
        print("❌ Invalid data: Site name or assets are empty.")
        return

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(TARGET_SHEET_NAME)

    existing_records = sheet.get_all_values()
    existing_df = pd.DataFrame(existing_records[1:], columns=existing_records[0])

    new_rows = []
    for asset_type, asset_name in zip(asset_types, asset_names):
        exists = (
            (existing_df["Site"] == site_name)
            & (existing_df["Asset Name"] == asset_name)
        ).any()
        if not exists:
            new_rows.append([site_name, asset_type, asset_name])

    if new_rows:
        print(f"✅ Uploading {len(new_rows)} new assets for site: {site_name}")
        sheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    else:
        print("🟡 No new assets to upload — all entries already exist.")
