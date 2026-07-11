# Srikara Hospitals — Cluster KPI Dashboard

A multi-page Streamlit app that turns the `Unit_Tracker` Google Sheet into
five levels of dashboards: Executive → Department → Quality → Doctor → Cluster.

## 1. Project structure

```
hospital_dashboard/
├── app.py                          # Level 1: Executive Dashboard (home page)
├── utils.py                        # Shared data loading + UI components
├── log_snapshot_cli.py             # Scheduled script to build trend history
├── requirements.txt
├── .streamlit/
│   └── secrets.toml.example        # Rename to secrets.toml and fill in
└── pages/
    ├── 1_OP_Dashboard.py
    ├── 2_IP_Dashboard.py
    ├── 3_ICU_Dashboard.py
    ├── 4_OT_Dashboard.py
    ├── 5_Billing_Dashboard.py
    ├── 6_Pharmacy_Dashboard.py
    ├── 7_Lab_Dashboard.py
    ├── 8_Radiology_Dashboard.py
    ├── 9_ER_Dashboard.py
    ├── 10_Quality_Dashboard.py     # Level 3
    ├── 11_Doctor_Dashboard.py      # Level 4 (MS sheet)
    └── 12_Cluster_Dashboard.py     # Level 5 (multi-hospital)
```

Streamlit automatically turns every file in `pages/` into a sidebar nav item,
in filename order — that's why they're numbered.

## 2. One-time setup

### a) Google Cloud service account (so the app can read your Sheet)
1. Go to console.cloud.google.com → create/select a project.
2. Enable the **Google Sheets API** and **Google Drive API**.
3. Create a **Service Account**, then create a JSON key for it and download it.
4. Open your `Unit_Tracker` Google Sheet → **Share** → paste the service
   account's email (looks like `xxx@xxx.iam.gserviceaccount.com`) → give it
   **Viewer** access (Editor if you want the "Log snapshot" buttons to work).

### b) Fill in secrets
Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste
in your Sheet ID (the long string in the sheet's URL) and the contents of the
service account JSON key.

### c) Install dependencies
```bash
pip install -r requirements.txt
```

### d) Run locally
```bash
streamlit run app.py
```

## 3. Enabling trend charts (important)

Your current sheets only store **today's snapshot** (Today / MTD columns),
not a history of past days — so there's nothing to draw a line chart from
yet. Two ways to fix this:

- **Manual**: each page has a "Log today's snapshot into History" button —
  click it once a day and a `History` tab gets a new row per metric.
- **Automatic (recommended)**: schedule `log_snapshot_cli.py` to run once a
  day, e.g. as a GitHub Actions workflow:

```yaml
# .github/workflows/daily_snapshot.yml
on:
  schedule:
    - cron: "0 18 * * *"   # runs daily at 11:30 PM IST
jobs:
  log:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: python log_snapshot_cli.py
        env:
          SHEET_ID: ${{ secrets.SHEET_ID }}
          GOOGLE_APPLICATION_CREDENTIALS: service_account.json
        # decode a base64 GitHub secret into service_account.json in a prior step
```

Once a few days of history accumulate, every trend chart in the app starts
populating automatically.

## 4. Deploying to Streamlit Community Cloud
1. Push this folder to a GitHub repo (add `.streamlit/secrets.toml` to
   `.gitignore` — never commit real credentials).
2. Go to share.streamlit.io → New app → point it at `app.py` in your repo.
3. In **App settings → Secrets**, paste the contents of your local
   `secrets.toml`.
4. Deploy. Your pages menu (department dashboards, Quality, Doctor, Cluster)
   appears automatically in the sidebar.

## 5. Setting up the Cluster Dashboard
The Cluster page expects every hospital/unit to keep its own copy of this
same workbook (same tab names, same layout). Add each hospital's Sheet ID to
the `[cluster]` section of `secrets.toml` — see the example file. No code
changes needed to add a new hospital, just a new line in secrets.

## 6. Glossary

| Term | Meaning |
|---|---|
| OP | Outpatient — patients seen without being admitted |
| IP | Inpatient — patients admitted to a bed |
| ER | Emergency Room |
| OT | Operation Theatre (surgery) |
| ICU | Intensive Care Unit |
| Footfall | Total number of patient visits |
| Census | Number of patients currently admitted |
| MTD | Month-to-Date — running total for the current month |
| TAT | Turnaround Time — how long a process takes end-to-end |
| ALOS / LOS | Average Length of Stay / Length of Stay |
| LAMA | Left Against Medical Advice |
| MLC | Medico-Legal Case |
| HAI | Hospital-Acquired Infection |
| NABH | National Accreditation Board for Hospitals & Healthcare Providers (India) |
| Bed Occupancy % | Beds currently occupied ÷ total beds available |
| OT Utilization % | Time OT is actually used ÷ time OT is available |
| Case Start Delay | How late a surgery starts vs. its scheduled time |
| Conversion % | e.g. OP → IP: share of outpatients who get admitted |

## 7. Data model recap

- **Snapshot ("Incharge") sheets** — OP, IP, ICU, OT, Billing, Pharmacy, Lab,
  Radiology, ER — filled daily by each department, source of truth.
- **Roll-up sheets** — Medical Admin, Unit Head, IT — same numbers, repeated
  for different audiences, with Medical Admin adding Targets.
- **Quality Head** — clinical/accreditation metrics, separate from throughput.
- **MS** — doctor-wise OP/IP volumes.
- **History** (created by this app) — the missing piece that turns snapshots
  into trends.
