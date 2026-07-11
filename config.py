"""
config.py
---------
All the settings for the dashboard live here.
If the Google Sheet ever changes, this is the ONLY file you should need to edit.
"""

# The long ID in your Google Sheet URL (the part between /d/ and /edit)
SHEET_ID = "1PCEbzi2RLDSV--bbDwaRMob2nU33PULlyjJp9Xwwv9M"

# The GID of the master "Unit Tracker" tab (the one with every department listed).
# You can see this number in the URL after gid= when that tab is open.
MASTER_GID = "143552182"

SHEET_GIDS = {
    # "OP Incharge": "PASTE_GID_HERE",
    # "IP Incharge": "PASTE_GID_HERE",
    # "ICU Incharge": "PASTE_GID_HERE",
    # "ER": "PASTE_GID_HERE",
    # "OT Incharge": "PASTE_GID_HERE",
    # "Billing": "PASTE_GID_HERE",
    # "Pharmacy": "PASTE_GID_HERE",
    # "Lab": "PASTE_GID_HERE",
    # "Radiology": "PASTE_GID_HERE",
    # "Quality Head": "PASTE_GID_HERE",
    # "MS": "PASTE_GID_HERE",
    # "Medical Admin": "PASTE_GID_HERE",
    # "Unit Head": "PASTE_GID_HERE",
    # "IT": "PASTE_GID_HERE",
}

DEPARTMENTS = [
    {"name": "OPD Operations",     "owner": "OP Incharge",  "icon": "🩺", "page": "pages/01_OPD_Operations.py"},
    {"name": "IP Operations",      "owner": "IP Incharge",  "icon": "🛏️", "page": "pages/02_IP_Operations.py"},
    {"name": "ICU Operations",     "owner": "ICU Incharge", "icon": "❤️‍🩹", "page": "pages/03_ICU_Operations.py"},
    {"name": "Emergency",          "owner": "ER",           "icon": "🚑", "page": "pages/04_Emergency.py"},
    {"name": "OT Operations",      "owner": "OT Incharge",  "icon": "🔪", "page": "pages/05_OT_Operations.py"},
    {"name": "Billing & Revenue",  "owner": "Billing",      "icon": "💵", "page": "pages/06_Billing_Revenue.py"},
    {"name": "Pharmacy",           "owner": "Pharmacy",     "icon": "💊", "page": "pages/07_Pharmacy.py"},
    {"name": "Laboratory",         "owner": "Lab",          "icon": "🧪", "page": "pages/08_Laboratory.py"},
    {"name": "Radiology",          "owner": "Radiology",    "icon": "🩻", "page": "pages/09_Radiology.py"},
    {"name": "Clinical Quality",   "owner": "Quality Head", "icon": "✅", "page": "pages/10_Clinical_Quality.py"},
    {"name": "Medical Staff",      "owner": "MS",           "icon": "👩‍⚕️", "page": "pages/11_Medical_Staff.py"},
]

CACHE_TTL_SECONDS = 300  # 5 minutes
