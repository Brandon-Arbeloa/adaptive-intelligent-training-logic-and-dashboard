from config import REPORT_SHEET

def read_existing_column_a(ws):
    values = ws.get_values('A1:A1000')
    return [row[0] for row in values if row]

def write_if_changed(ws, title, lines):
    new_content = [title, ''] + lines
    old_content = read_existing_column_a(ws)
    if old_content == new_content:
        return False
    ws.clear()
    rows = [[title]] + [['']] + [[s] for s in lines]
    ws.update('A1', rows, value_input_option='RAW')
    ws.format('A1', {'textFormat': {'bold': True, 'fontSize': 12}})
    return True

def ensure_report_sheet(ss):
    for w in ss.worksheets():
        if w.title == REPORT_SHEET:
            return w
    return ss.add_worksheet(title=REPORT_SHEET, rows='1000', cols='2')
