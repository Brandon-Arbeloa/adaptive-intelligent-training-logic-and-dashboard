#!/usr/bin/env python3
"""
Training Dashboard - ACTUAL Professional Dark Theme
Like the screenshot you showed
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import gspread
from pathlib import Path
import sys

# Fix imports
BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

try:
    from config import CRED_PATH, SPREADSHEET_URL
except ImportError:
    CRED_PATH = str(BASE_DIR / 'credentials.json')
    SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1Js2s7s95miuUzdn44guWnGuML2kxYzN3kG_jsEdWu68/edit'

# Page config
st.set_page_config(
    page_title="Training Command Center",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# DARK THEME CSS - Like your screenshot
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    
    /* Dark theme like the screenshot */
    .stApp {
        background: #1a1a2e;
    }
    
    .main {
        background: #1a1a2e;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .dashboard-title {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        color: white;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .dashboard-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: rgba(255,255,255,0.7);
        margin-top: 0.5rem;
    }
    
    /* Metric cards */
    .metric-container {
        background: #0f0f23;
        border: 1px solid #2a2a3e;
        border-radius: 8px;
        padding: 1.5rem;
        height: 100%;
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        color: white;
        line-height: 1;
    }
    
    .metric-delta {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-delta.positive {
        color: #10b981;
    }
    
    .metric-delta.negative {
        color: #ef4444;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .status-badge.on-track {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid #10b981;
    }
    
    /* Charts */
    .chart-container {
        background: #0f0f23;
        border: 1px solid #2a2a3e;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    /* Week progress bar */
    .week-progress {
        display: flex;
        gap: 0.25rem;
        margin: 2rem 0;
    }
    
    .week-bar {
        flex: 1;
        height: 8px;
        background: #2a2a3e;
        position: relative;
    }
    
    .week-bar.complete {
        background: #667eea;
    }
    
    .week-bar.current {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Data table */
    .data-table {
        background: #0f0f23;
        border: 1px solid #2a2a3e;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .data-table th {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 0.75rem;
        border-bottom: 1px solid #2a2a3e;
    }
    
    .data-table td {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        color: #e5e5e5;
        padding: 0.75rem;
        border-bottom: 1px solid #1a1a2e;
    }
    
    /* Override Streamlit defaults */
    .stMetric {
        background: transparent !important;
    }
    
    [data-testid="metric-container"] {
        background: #0f0f23;
        border: 1px solid #2a2a3e;
        border-radius: 8px;
        padding: 1.5rem;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        color: white;
    }
    
    .st-emotion-cache-1kyxreq {
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_resource
def init_connection():
    gc = gspread.service_account(filename=CRED_PATH)
    return gc.open_by_url(SPREADSHEET_URL)

@st.cache_data(ttl=60)
def load_data():
    ss = init_connection()
    all_data = []
    
    for week_num in range(1, 9):
        try:
            sheet = ss.worksheet(f"Week {week_num}")
            data = sheet.get_all_values()
            
            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
                df['Week'] = week_num
                
                for _, row in df.iterrows():
                    if row.get('Exercise') and str(row['Exercise']).strip() and row['Exercise'] != 'Exercise':
                        sets_str = str(row.get('Sets', '0'))
                        reps_str = str(row.get('Reps', '0'))
                        
                        # Parse sets
                        if '-' in sets_str:
                            parts = sets_str.split('-')
                            sets = (float(parts[0]) + float(parts[1])) / 2 if len(parts) == 2 else 0
                        else:
                            try:
                                sets = float(sets_str)
                            except:
                                sets = 0
                        
                        # Parse reps
                        if '-' in reps_str:
                            parts = reps_str.split('-')
                            reps = (float(parts[0]) + float(parts[1])) / 2 if len(parts) == 2 else 0
                        else:
                            try:
                                reps = float(reps_str)
                            except:
                                reps = 0
                        
                        all_data.append({
                            'Week': week_num,
                            'Muscle Group': row.get('Muscle Group', ''),
                            'Exercise': row['Exercise'],
                            'Sets': sets,
                            'Reps': reps,
                            'Volume': sets * reps
                        })
        except:
            pass
    
    return pd.DataFrame(all_data)

def main():
    # Load data
    try:
        df = load_data()
        if df.empty:
            st.error("No training data found")
            st.stop()
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()
    
    # Header
    st.markdown("""
        <div class="dashboard-header">
            <h1 class="dashboard-title">INGENIUM PROGRESSIO</h1>
            <p class="dashboard-subtitle">The Genius of Progression • 8-Week Adaptive Training Program</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Calculate metrics
    current_week = df['Week'].max()
    total_volume = df['Volume'].sum()
    total_exercises = len(df)
    completion = (current_week / 8) * 100
    
    # Top metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">📅 Week</div>
                <div class="metric-value">{current_week} of 8</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">🔥 Total Volume</div>
                <div class="metric-value">{int(total_volume):,}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">💪 Exercises Done</div>
                <div class="metric-value">{total_exercises}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">📊 Progress</div>
                <div class="metric-value">{int(completion)}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Status</div>
                <div style="padding-top: 0.5rem;">
                    <span class="status-badge on-track">✅ On Track</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Week progress bar
    week_html = '<div class="week-progress">'
    for week in range(1, 9):
        if week < current_week:
            week_html += '<div class="week-bar complete"></div>'
        elif week == current_week:
            week_html += '<div class="week-bar current"></div>'
        else:
            week_html += '<div class="week-bar"></div>'
    week_html += '</div>'
    st.markdown(week_html, unsafe_allow_html=True)
    
    # Charts section
    st.markdown("<h2 style='color: white; font-family: Inter; font-size: 1.5rem; margin-top: 2rem;'>8-WEEK TRAINING PROGRESSION (WEEK 3 OF 8)</h2>", unsafe_allow_html=True)
    
    # Weekly volume chart
    weekly = df.groupby('Week')['Volume'].sum().reset_index()
    
    fig = go.Figure()
    
    # Add bars
    colors = ['#667eea' if w <= current_week else '#2a2a3e' for w in weekly['Week']]
    
    fig.add_trace(go.Bar(
        x=weekly['Week'],
        y=weekly['Volume'],
        marker_color=colors,
        text=weekly['Volume'],
        textposition='outside',
        textfont=dict(color='white', size=12, family='Inter'),
        hovertemplate='Week %{x}<br>Volume: %{y}<extra></extra>'
    ))
    
    # Add current week line
    if current_week <= 8:
        fig.add_vline(
            x=current_week + 0.5,
            line_dash="dash",
            line_color="#764ba2",
            annotation_text=f"Current Week {current_week}",
            annotation_position="top",
            annotation_font=dict(color='#764ba2', size=10)
        )
    
    fig.update_layout(
        plot_bgcolor='#0f0f23',
        paper_bgcolor='#0f0f23',
        font=dict(color='#666', family='Inter'),
        xaxis=dict(
            title='WEEK',
            showgrid=False,
            color='#666',
            tickmode='linear',
            tick0=1,
            dtick=1
        ),
        yaxis=dict(
            title='VOLUME',
            showgrid=True,
            gridcolor='#2a2a3e',
            color='#666'
        ),
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Weekly summary table
    st.markdown("<h2 style='color: white; font-family: Inter; font-size: 1.5rem; margin-top: 2rem;'>WEEKLY SUMMARY</h2>", unsafe_allow_html=True)
    
    # Create summary by week
    summary = df.groupby(['Week', 'Muscle Group'])['Exercise'].count().reset_index()
    summary.columns = ['Week', 'Muscle Group', 'Exercises']
    
    # Display as grid
    for week in range(1, min(current_week + 1, 9)):
        week_data = summary[summary['Week'] == week]
        if not week_data.empty:
            status = "✅ Complete" if week < current_week else "🟡 Current" if week == current_week else "⏰ Upcoming"
            
            st.markdown(f"""
                <div style='background: #0f0f23; border: 1px solid #2a2a3e; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='color: white; font-weight: 600;'>Week {week}</span>
                        <span style='color: #666;'>{status}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()