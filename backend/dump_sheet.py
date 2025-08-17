#!/usr/bin/env python3
"""
Actually check what's in the sheet and print everything
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL

gc = gspread.service_account(filename=CRED_PATH)
ss = gc.open_by_url(SPREADSHEET_URL)

print("="*60)
print("FULL DATA DUMP - WEEK 1")
print("="*60)

sheet = ss.worksheet("Week 1")

# Get ALL data in the sheet (first 50 rows, first 10 columns)
data = sheet.get("A1:J50")

print(f"Total rows retrieved: {len(data)}")
print()

# Print everything
for i, row in enumerate(data, start=1):
    if any(cell for cell in row):  # If row has any data
        print(f"Row {i}: {row}")
    if i > 20 and not any(row[1:3] if len(row) > 2 else []):
        break  # Stop after 20 rows or when no exercise data

print("\n" + "="*60)
print("Now tell me what columns have:")
print("- Muscle Groups")
print("- Exercises") 
print("- Sets")
print("- Reps")
print("="*60)