# Python 3.14 Compatibility

This package has been updated for **Python 3.14 (64-bit) on Windows**. The dependency versions in `requirements.txt` have Python 3.14-compatible wheels, so you should not need Visual Studio Build Tools or a second Python installation.

For a clean Windows setup, delete any old `.venv`, create it again with your normal `python` command, activate it, upgrade pip, and install requirements:

```powershell
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Then verify:

```powershell
python --version
python -c "import pandas, numpy, matplotlib; print('pandas', pandas.__version__); print('numpy', numpy.__version__); print('matplotlib', matplotlib.__version__)"
```

---

# Traya Retail Activation & Conversion Email Flash

Email-first retail decision analytics. No standalone dashboard is required.

## What it answers
1. Is conversion healthy? Where is weak conversion, and is the likely issue engagement, conversion quality or availability?
2. Where is there additional sales headroom despite healthy opportunity, engagement and conversion?
3. Which outlets have weak relevant shopping and may need to be reassessed?
4. Which outlet-SKU combinations need replenishment based on availability, days cover, safety stock and reorder point?

## Architecture
Google Drive workbook -> Cloud Run (Python/pandas) -> diagnostic rules + PNG visuals + HTML tables -> Apps Script -> Gmail.

Only the `Traya Hair Care` sheet is loaded. Other sheets are ignored.

## Key analytical definitions
- Outlet conversion = Shoppers Sold To / Hair Care Shoppers
- Interaction rate = Promoter Interacted With / Hair Care Shoppers
- Promoter conversion = Shoppers Sold To / Promoter Interactions
- Relevant shopper rate = Hair Care Shoppers / Walk-ins
- Peer benchmark = median of same City + Channel outlets
- Availability = 1 - (closing-stock-zero SKU-days / eligible SKU-days)
- Safety stock = z * std(daily demand) * sqrt(lead time)
- Reorder point = avg daily demand * lead time + safety stock
- Scale headroom = relevant shoppers * (peer top-quartile conversion - current conversion) * units/buyer

`REPLENISHMENT_LEAD_TIME_DAYS` defaults to 2 and `SAFETY_STOCK_Z` to 1.65 (approx. 95% service factor). Change these to match the business.

Promoter-supported vs outlet-pull is treated as a signal, not causal proof. It compares the same outlet's conversion on high- vs low-engagement days.

## Local test on Windows
1. Put the workbook at `data/traya_input.xlsx` OR set LOCAL_DATA_PATH to your existing workbook.
2. In PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
$env:LOCAL_DATA_PATH="C:\path\to\SPG_Dummy_Promoter_Data_Traya_WholeTruth(2).xlsx"
$env:APP_API_KEY="local-test-key"
python app.py
```

Flask dev server defaults to port 5000. Test:

```powershell
curl.exe -H "X-API-Key: local-test-key" "http://127.0.0.1:5000/report?cadence=weekly"
```

## Google Cloud setup
Enable Cloud Run, Cloud Build, Artifact Registry and Drive API.

```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com drive.googleapis.com

gcloud iam service-accounts create traya-retail-flash --display-name="Traya Retail Flash"
```

Create a Google Drive folder, upload the workbook, and share that folder as Viewer with:
`traya-retail-flash@YOUR_PROJECT_ID.iam.gserviceaccount.com`

Copy the Drive folder ID from its URL.

Generate an API key:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Deploy:
```powershell
gcloud run deploy traya-retail-flash `
  --source . `
  --region asia-south1 `
  --allow-unauthenticated `
  --service-account traya-retail-flash@YOUR_PROJECT_ID.iam.gserviceaccount.com `
  --set-env-vars DRIVE_FOLDER_ID=YOUR_FOLDER_ID,APP_API_KEY=YOUR_KEY,REPLENISHMENT_LEAD_TIME_DAYS=2,SAFETY_STOCK_Z=1.65
```

The service URL can be public because `/report` still requires the X-API-Key. `/health` contains no business data.

## Apps Script setup
1. Create a new Google Apps Script project.
2. Paste `apps_script/Code.gs`.
3. Project Settings -> Script Properties:
   - CLOUD_RUN_URL = Cloud Run service URL (no trailing slash)
   - APP_API_KEY = same key used above
   - RECIPIENTS = comma-separated Gmail addresses
4. Run `testWeeklyFlash()` once and authorize.
5. Run `createWeeklyTrigger()` for Monday ~8 AM IST.
6. Optional: run `createDailyTrigger()` for a daily ~8 PM exception flash.

## Email structure
- 4 headline KPIs: conversion, relevant shoppers, availability, offtake/manday
- What requires action? (max 5 outlets)
- Where can we sell more? (max 5 outlets)
- Are we in the right outlets? (max 5 outlets)
- Availability actions (max 5 outlet-SKU rows)
- 2 PNG visuals: funnel + conversion diagnostic matrix

The HTML uses tables + inline styles for Gmail/Outlook compatibility; charts are PNGs embedded as CID images.
