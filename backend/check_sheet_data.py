#!/usr/bin/env python3
"""
Quick script to see what's actually in the Google Sheet
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL

gc = gspread.service_account(filename=CRED_PATH)
ss = gc.open_by_url(SPREADSHEET_URL)

print("="*60)
print("CHECKING YOUR ACTUAL SHEET DATA")
print("="*60)

# Check each week
for week_num in range(1, 9):
    try:
        sheet = ss.worksheet(f"Week {week_num}")
        
        # Get ALL data to see what's there
        all_data = sheet.get_all_values()
        
        print(f"\n📊 Week {week_num}:")
        print(f"   Total rows: {len(all_data)}")
        
        if all_data:
            # Show headers
            print(f"   Headers: {all_data[0][:10]}")  # First 10 columns
            
            # Count non-empty data rows
            data_rows = 0
            for row in all_data[1:]:  # Skip header
                if any(cell.strip() for cell in row):  # If any cell has content
                    data_rows += 1
            
            print(f"   Data rows: {data_rows}")
            
            # Show a sample data row
            if len(all_data) > 1:
                print(f"   Sample row 2: {all_data[1][:10]}")
            if len(all_data) > 2:
                print(f"   Sample row 3: {all_data[2][:10]}")
                
    except Exception as e:
        print(f"\n❌ Week {week_num}: Not found or error: {e}")

print("\n" + "="*60)
print("Now I know what columns your data is in!")
print("="*60)