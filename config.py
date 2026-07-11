"""
config.py

Fill this in with your own Sheet ID and each tab's GID — no Google login,
no service account, no JSON key needed. This works because the sheet is
shared as "Anyone with the link can view."

HOW TO GET SHEET_ID:
Open your Google Sheet. The URL looks like:
    https://docs.google.com/spreadsheets/d/1AbCXyz9876543210LongString/edit
The long string between /d/ and /edit is your SHEET_ID.

HOW TO GET EACH TAB'S GID:
Click on a tab at the bottom of your Google Sheet (e.g. "OP Incharge").
Look at the URL — it now ends with something like #gid=123456789
Copy that number (just the digits) into the matching line below.
The first/leftmost tab is usually gid=0.
"""

SHEET_ID = "PUT_YOUR_SHEET_ID_HERE"

SHEET_GIDS = {
    "Medical Admin": 0,
    "Unit Head": 0,
    "Quality Head": 0,
    "IT": 0,
    "OP Incharge": 0,
    "Radiology": 0,
    "Billing": 0,
    "Pharmacy": 0,
    "Lab": 0,
    "ER": 0,
    "OT Incharge": 0,
    "IP Incharge": 0,
    "ICU Incharge": 0,
    "MS": 0,
}

# Only needed for the Cluster Dashboard, once you have more than one hospital
# each keeping their own copy of this workbook (also shared as "Anyone with
# the link can view"):
CLUSTER_HOSPITALS = {
    # "Hospital A": "sheet-id-for-hospital-a",
    # "Hospital B": "sheet-id-for-hospital-b",
}
