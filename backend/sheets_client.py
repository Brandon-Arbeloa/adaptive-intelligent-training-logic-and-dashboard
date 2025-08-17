import time, gspread
from gspread.exceptions import APIError
from config import CRED_PATH, SPREADSHEET_URL

def _backoff(call, *args, **kwargs):
    delay = 1.0
    for _ in range(5):
        try:
            return call(*args, **kwargs)
        except APIError as e:
            if getattr(e, "response", None) and e.response.status_code in (429, 500, 503):
                time.sleep(delay)
                delay *= 2
            else:
                raise
    return call(*args, **kwargs)

def open_spreadsheet():
    gc = gspread.service_account(filename=CRED_PATH)
    return _backoff(gc.open_by_url, SPREADSHEET_URL)

def batch_get_ranges(ss, ranges):
    """
    Returns list of rows per range (aligned to input order), using gspread's values_batch_get.
    Each item is a list[list[str]] like Worksheet.get('A1:D').
    """
    resp = _backoff(ss.values_batch_get, ranges=ranges)
    value_ranges = resp.get("valueRanges", [])
    
    # Map by range to preserve order
    by_range = {vr.get("range"): vr.get("values", []) for vr in value_ranges}
    
    out = []
    for r in ranges:
        # Try exact match first
        vals = by_range.get(r)
        if vals is None:
            # Fallback: find a key whose range ends with our r
            for k, v in by_range.items():
                if k.endswith(r):
                    vals = v
                    break
        out.append(vals or [])
    
    return out