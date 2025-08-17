#!/usr/bin/env python3
"""
Check what's ACTUALLY in the Google Sheet columns
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL

gc = gspread.service_account(filename=CRED_PATH)
ss = gc.open_by_url(SPREADSHEET_URL)

print("="*60)
print("CHECKING GOOGLE SHEET (not Excel)")
print("="*60)

# Check Week 1
sheet = ss.worksheet("Week 1")

# Get the first 10 rows, all columns
data = sheet.get("A1:M10")

print("\nWEEK 1 - First 10 rows:")
print("-"*60)

# Print headers
if data:
    print("HEADERS:", data[0])
    print()
    
    # Print data rows
    for i, row in enumerate(data[1:], start=2):
        if any(cell for cell in row):  # If row has any data
            print(f"Row {i}: {row[:7]}")  # Show first 7 columns (A-G)

# Now check what's in columns D and E specifically
print("\n" + "="*60)
print("COLUMNS D & E SPECIFICALLY:")
print("-"*60)

d_e_data = sheet.get("D1:E20")
for i, row in enumerate(d_e_data, start=1):
    if i == 1:
        print(f"Headers: {row}")
    elif any(row):
        print(f"Row {i}: {row}")

print("\n" + "="*60)
print("This is what's ACTUALLY in your Google Sheet!")
print("="*60)