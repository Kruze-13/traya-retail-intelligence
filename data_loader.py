import io, os
import pandas as pd
from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SHEET = os.getenv('TRAYA_SHEET_NAME', 'Traya Hair Care')

def _read_excel(source):
    return pd.read_excel(source, sheet_name=SHEET, header=4)

def load_traya_data():
    local = os.getenv('LOCAL_DATA_PATH', '').strip()
    if local and os.path.exists(local):
        df = _read_excel(local)
        return df, os.path.basename(local)

    folder_id = os.getenv('DRIVE_FOLDER_ID', '').strip()
    if not folder_id:
        raise RuntimeError('Set LOCAL_DATA_PATH or DRIVE_FOLDER_ID.')
    creds, _ = default(scopes=['https://www.googleapis.com/auth/drive.readonly'])
    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    q = f"'{folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
    files = service.files().list(q=q, orderBy='modifiedTime desc', pageSize=20,
                                 fields='files(id,name,mimeType,modifiedTime)').execute().get('files', [])
    excel_files = [f for f in files if f['name'].lower().endswith(('.xlsx','.xlsm','.xlsb'))]
    if not excel_files:
        raise RuntimeError('No Excel workbook found in Drive folder.')
    f = excel_files[0]
    req = service.files().get_media(fileId=f['id'])
    buf = io.BytesIO(); dl = MediaIoBaseDownload(buf, req); done=False
    while not done:
        _, done = dl.next_chunk()
    buf.seek(0)
    df = _read_excel(buf)
    return df, f['name']
