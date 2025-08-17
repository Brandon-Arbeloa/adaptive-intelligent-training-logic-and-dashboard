import os, time
import streamlit as st
from dotenv import load_dotenv
import gspread
from gspread.exceptions import APIError
import plotly.express as px

load_dotenv()

SPREADSHEET_URL = os.getenv('SPREADSHEET_URL', '')
CRED_PATH       = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'creds/service_account.json')
REPORT_SHEET    = os.getenv('REPORT_SHEET_NAME', 'Rotation Report')
WEEK_SHEETS     = [s.strip() for s in os.getenv('WEEK_SHEETS','Week 1,Week 2').split(',')]

st.set_page_config(page_title='Adaptive Training Dashboard', layout='wide')
st.title('🏋️ Intelligent Adaptive Training Dashboard')

@st.cache_resource
def open_sheet():
    gc = gspread.service_account(filename=CRED_PATH)
    return gc.open_by_url(SPREADSHEET_URL)

def backoff(call, *args, **kwargs):
    delay=0.5
    for _ in range(5):
        try: return call(*args, **kwargs)
        except APIError as e:
            if getattr(e, 'response', None) and e.response.status_code in (429,500,503):
                time.sleep(delay); delay*=2
            else: raise
    return call(*args, **kwargs)

def read_rotation_report(ss):
    try:
        ws = ss.worksheet(REPORT_SHEET)
        vals = backoff(ws.get_values, 'A1:A1000')
        return [row[0] for row in vals if row]
    except Exception as e:
        return []

def read_week_data(ss):
    rows = []
    titles = {w.title for w in ss.worksheets()}
    for name in WEEK_SHEETS:
        if name not in titles: continue
        ws = ss.worksheet(name)
        vals = ws.get('A2:D')
        wk = int(name.split()[-1])
        for r in vals:
            r = (r+['','','',''])[:4]
            mg, ex, sets_, reps_ = r
            ex = (ex or '').strip()
            if not ex: continue
            try: sets = float(sets_) if str(sets_).strip() else 0.0
            except: sets = 0.0
            try: reps = float(reps_) if str(reps_).strip() else 0.0
            except: reps = 0.0
            rows.append({'week':wk,'muscleGroup':(mg or '').strip() or 'Unknown','exercise':ex,'volume':sets*reps})
    return rows

if not SPREADSHEET_URL or not os.path.exists(CRED_PATH):
    st.warning('Configure SPREADSHEET_URL and GOOGLE_APPLICATION_CREDENTIALS in .env; place service_account.json in creds/.')
    st.stop()

ss = open_sheet()

col1, col2 = st.columns([1,2])
with col1:
    st.subheader('📄 Rotation Report')
    lines = read_rotation_report(ss)
    if lines:
        st.text('\n'.join(lines))
    else:
        st.info('No Rotation Report yet. Run the backend job.')

with col2:
    st.subheader('📈 Exercise Frequency (by weeks used)')
    rows = read_week_data(ss)
    if rows:
        freq = {}
        for r in rows:
            ex = r['exercise']
            freq.setdefault(ex, set()).add(r['week'])
        chart = sorted([(ex, len(wks)) for ex, wks in freq.items()], key=lambda t: t[1], reverse=True)[:20]
        if chart:
            df = {'Exercise':[t[0] for t in chart], 'Weeks Used':[t[1] for t in chart]}
            fig = px.bar(df, x='Exercise', y='Weeks Used')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('No week rows found.')
