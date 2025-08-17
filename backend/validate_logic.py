#!/usr/bin/env python3
"""
Validation script - TEST the logic before applying to real data
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL
import sys
sys.path.append('.')
from complete_adaptive_logic import parse_range_or_int, pick_value_from_range, resolve_final_number

def test_range_parsing():
    """Test the range parsing function"""
    print("\n🧪 TESTING RANGE PARSER")
    print("="*50)
    
    test_cases = [
        ("3-5", (3, 5), "Valid range"),
        ("6-8", (6, 8), "Valid range"),
        ("10-12", (10, 12), "Valid range"),
        ("3", (3, 3), "Single number"),
        ("180-240", (180, 240), "Large range"),
        ("3/5", (None, None), "Date format - should fail"),
        ("3–6", (3, 6), "En dash range"),
        ("3 - 5", (3, 5), "Range with spaces"),
        ("Sets", (None, None), "Text - should fail"),
        ("", (None, None), "Empty - should fail"),
    ]
    
    passed = 0
    failed = 0
    
    for input_val, expected, description in test_cases:
        result = parse_range_or_int(input_val)
        if result == expected:
            print(f"  ✅ '{input_val}' -> {result} ({description})")
            passed += 1
        else:
            print(f"  ❌ '{input_val}' -> {result}, expected {expected} ({description})")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0

def test_value_selection():
    """Test the progressive value selection"""
    print("\n🧪 TESTING VALUE SELECTION")
    print("="*50)
    
    print("\nProgressive mode (3-5 range over 8 weeks):")
    for week in range(1, 9):
        val = pick_value_from_range(3, 5, week, 8, "progressive")
        print(f"  Week {week}: {val}")
    
    print("\nProgressive mode (6-8 reps over 8 weeks):")
    for week in range(1, 9):
        val = pick_value_from_range(6, 8, week, 8, "progressive")
        print(f"  Week {week}: {val}")
    
    print("\nDifferent modes for range 10-15:")
    for mode in ["low", "mid", "high", "progressive"]:
        vals = []
        for week in [1, 4, 8]:
            val = pick_value_from_range(10, 15, week, 8, mode)
            vals.append(f"W{week}={val}")
        print(f"  {mode:12s}: {', '.join(vals)}")

def validate_logic_sheets():
    """Check what's actually in the logic sheets"""
    print("\n🧪 VALIDATING LOGIC SHEETS")
    print("="*50)
    
    gc = gspread.service_account(filename=CRED_PATH)
    ss = gc.open_by_url(SPREADSHEET_URL)
    
    # Check Logic Engine
    try:
        sheet = ss.worksheet("Logic Engine")
        data = sheet.get("A1:G3")  # Get headers + 2 rows
        
        print("\n📊 Logic Engine Sample:")
        headers = data[0] if data else []
        print(f"  Headers: {headers}")
        
        if len(data) > 1:
            sample = data[1]
            if len(sample) >= 6:
                sets_val = sample[3]
                reps_val = sample[4]
                rest_val = sample[5]
                
                print(f"  Sample row: {sample[:6]}")
                print(f"  Sets value: '{sets_val}' -> {parse_range_or_int(sets_val)}")
                print(f"  Reps value: '{reps_val}' -> {parse_range_or_int(reps_val)}")
                print(f"  Rest value: '{rest_val}' -> {parse_range_or_int(rest_val)}")
    except Exception as e:
        print(f"  ❌ Error reading Logic Engine: {e}")
    
    # Check CategoryLogic
    try:
        sheet = ss.worksheet("CategoryLogic")
        data = sheet.get("A1:G3")
        
        print("\n📋 CategoryLogic Sample:")
        headers = data[0] if data else []
        print(f"  Headers: {headers}")
        
        if len(data) > 1:
            sample = data[1]
            if len(sample) >= 6:
                sets_val = sample[3]
                reps_val = sample[4]
                rest_val = sample[5]
                
                print(f"  Sample row: {sample[:6]}")
                print(f"  Sets value: '{sets_val}' -> {parse_range_or_int(sets_val)}")
                print(f"  Reps value: '{reps_val}' -> {parse_range_or_int(reps_val)}")
                print(f"  Rest value: '{rest_val}' -> {parse_range_or_int(rest_val)}")
    except Exception as e:
        print(f"  ❌ Error reading CategoryLogic: {e}")

def test_actual_data():
    """Test on actual Week 1 data without writing"""
    print("\n🧪 TESTING ON ACTUAL DATA (READ-ONLY)")
    print("="*50)
    
    gc = gspread.service_account(filename=CRED_PATH)
    ss = gc.open_by_url(SPREADSHEET_URL)
    
    try:
        sheet = ss.worksheet("Week 1")
        data = sheet.get("A2:F10")  # Get first 8 data rows
        
        print("\nWeek 1 - First few exercises:")
        print("-"*50)
        
        for row_idx, row in enumerate(data, start=2):
            if len(row) >= 3 and row[2]:  # Has exercise
                muscle = row[1] if len(row) > 1 else ""
                exercise = row[2]
                current_sets = row[3] if len(row) > 3 else ""
                current_reps = row[4] if len(row) > 4 else ""
                
                print(f"\nRow {row_idx}: {exercise} ({muscle})")
                print(f"  Current: Sets={current_sets}, Reps={current_reps}")
                
                # Test what we WOULD write
                if current_sets in ["3-5", "Sets"]:
                    print(f"  Would fix sets: '{current_sets}' -> {resolve_final_number('3-5', 1, 8, 'progressive')}")
                if current_reps in ["3-6", "Reps"]:
                    print(f"  Would fix reps: '{current_reps}' -> {resolve_final_number('6-8', 1, 8, 'low')}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("="*60)
    print("VALIDATION SUITE FOR ADAPTIVE LOGIC")
    print("="*60)
    
    # Run all tests
    test_range_parsing()
    test_value_selection()
    validate_logic_sheets()
    test_actual_data()
    
    print("\n" + "="*60)
    print("✅ VALIDATION COMPLETE!")
    print("\nIf everything looks good above, you can run:")
    print("  python complete_adaptive_logic.py")
    print("\nOr to force overwrite bad values:")
    print("  python complete_adaptive_logic.py force")

if __name__ == "__main__":
    main()