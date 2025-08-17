import json, pathlib
from backend.analyze import build_db, analyze, report_lines
from datetime import datetime

here = pathlib.Path(__file__).resolve().parent
rows = json.loads((here/'sample_rows.json').read_text())
db = build_db(rows)
over, bal, under, ideas = analyze(db)
lines = report_lines(db, over, bal, under, ideas, datetime.now().isoformat())
print('\n'.join(lines[:25]))
