import logging
import os
from datetime import datetime
from config import WEEK_SHEETS, LOG_PATH
from sheets_client import open_spreadsheet, batch_get_ranges
from analyze import parse_rows, build_db, analyze, report_lines
from report_writer import ensure_report_sheet, write_if_changed

# Create log directory if it doesn't exist
log_dir = os.path.dirname(LOG_PATH)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s')

def main():
    print("🔄 Starting rotation analysis...")
    logging.info("Starting rotation analysis...")
    
    try:
        ss = open_spreadsheet()
        print(f"✅ Connected to spreadsheet")
        
        # Build ranges for batch get
        available_sheets = {w.title for w in ss.worksheets()}
        print(f"📊 Available sheets: {available_sheets}")
        
        ranges = [f"{name}!B2:E" for name in WEEK_SHEETS if name in available_sheets]
        print(f"📋 Will check: {ranges}")
        
        if not ranges:
            print("❌ No Week sheets found.")
            logging.info("No Week sheets found.")
            return
    
        # Batch get all ranges at once
        batch = batch_get_ranges(ss, ranges)
        print(f"📦 Got {len(batch)} ranges")
        
        all_rows = []
        for rng, rows in zip(ranges, batch):
            sheet_name = rng.split("!")[0]
            parsed = parse_rows(sheet_name, rows)
            all_rows.extend(parsed)
            print(f"  {sheet_name}: {len(parsed)} exercises")
        
        if not all_rows:
            print("⚠️ No training rows present.")
            logging.info("No training rows present.")
            return
        
        print(f"🧠 Analyzing {len(all_rows)} total exercises...")
        db = build_db(all_rows)
        over, bal, under, ideas = analyze(db)
        lines = report_lines(db, over, bal, under, ideas, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ws = ensure_report_sheet(ss)
        updated = write_if_changed(ss, ws, "🧠 Automated Rotation Analysis", lines)
        logging.info("Report %s", "updated" if updated else "unchanged")
        
        print(f"✅ Analysis complete: {len(db)} exercises analyzed")
        print(f"   Overused: {len(over)}")
        print(f"   Balanced: {len(bal)}")
        print(f"   Underused: {len(under)}")
        print(f"Check the 'Rotation Report' sheet in your Google Sheets!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Error: {e}")
        raise
if __name__ == "__main__":
    main()