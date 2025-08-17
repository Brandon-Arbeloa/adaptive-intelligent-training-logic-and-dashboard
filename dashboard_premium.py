#!/usr/bin/env python3
"""
Premium Training Dashboard - Professional SaaS-Quality Design
Modern, dark theme with gradient accents - Looks like Strong/Hevy
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import gspread
from pathlib import Path
import sys
import numpy as np

# Fix imports
BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

try:
    from config import CRED_PATH, SPREADSHEET_URL
except ImportError:
    CRED_PATH = str(BASE_DIR / 'credentials.json')
    SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1Js2s7s95miuUzdn44guWnGuML2kxYzN3kG_jsEdWu68/edit'

# Page config - MUST BE FIRST
st.set_page_config(
    page_title="Adaptive Training System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional dark theme CSS with improved readability
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global dark theme with better contrast */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #141420;
        --bg-card: #1a1a28;
        --border-color: #2a2a3e;
        --text-primary: #ffffff;
        --text-secondary: #c8c8d8;  /* Lighter for better readability */
        --text-muted: #9898b0;  /* Lighter muted text */
        
        /* Gradient colors */
        --gradient-purple: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-blue: linear-gradient(135deg, #667eea 0%, #4a9eff 100%);
        --gradient-green: linear-gradient(135deg, #00c896 0%, #00e5a0 100%);
        --gradient-red: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%);
        
        /* Base colors for gradients */
        --purple-base: #440052;
        --blue-base: #040380;
        --green-base: #008000;
        --red-base: #c40000;
    }
    
    /* Main app background */
    .stApp {
        background: var(--bg-primary);
    }
    
    /* Sidebar styling - data heavy */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
        width: 320px !important;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header with gradient */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-left {
        flex: 1;
    }
    
    .app-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .app-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .header-stats {
        display: flex;
        gap: 2rem;
    }
    
    .header-stat {
        text-align: center;
    }
    
    .header-stat-value {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }
    
    .header-stat-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        color: rgba(255,255,255,0.8);
        margin-top: 0.25rem;
    }
    
    /* Metric cards with subtle gradients */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        height: 100%;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-purple);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    
    .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .metric-icon.purple {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-icon.blue {
        background: linear-gradient(135deg, #667eea 0%, #4a9eff 100%);
    }
    
    .metric-icon.green {
        background: linear-gradient(135deg, #00c896 0%, #00e5a0 100%);
    }
    
    .metric-icon.red {
        background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%);
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);  /* Better contrast */
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }
    
    .metric-change {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .metric-change.positive {
        color: #10b981;
    }
    
    .metric-change.negative {
        color: #ef4444;
    }
    
    /* Progress rings */
    .progress-ring {
        position: relative;
        width: 120px;
        height: 120px;
        margin: 0 auto;
    }
    
    .progress-ring svg {
        transform: rotate(-90deg);
    }
    
    .progress-value {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    /* Chart containers */
    .chart-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .chart-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }
    
    /* Week progress bar */
    .week-progress-container {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .week-progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .week-progress-title {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .week-progress-value {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
    }
    
    .week-bars {
        display: flex;
        gap: 4px;
        margin-top: 1rem;
    }
    
    .week-bar {
        flex: 1;
        height: 40px;
        background: var(--bg-secondary);
        border-radius: 8px;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .week-bar:hover {
        transform: translateY(-2px);
    }
    
    .week-bar.completed {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .week-bar.current {
        background: linear-gradient(135deg, #00c896 0%, #00e5a0 100%);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    .week-bar-label {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
        opacity: 0.9;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .sidebar-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }
    
    /* Custom select boxes and tabs */
    .stSelectbox > div > div {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }
    
    .stSelectbox label {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card);
        padding: 0.5rem;
        border-radius: 12px;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-muted);
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-secondary);
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"]:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Data tables */
    .dataframe {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    .dataframe th {
        background: var(--bg-secondary) !important;
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.5px !important;
    }
    
    .dataframe td {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        border-color: var(--border-color) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }
    
    /* Override Streamlit metric styling */
    [data-testid="metric-container"] {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.25rem;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: var(--text-secondary);
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.75rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.375rem 0.75rem;
        border-radius: 999px;
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-badge.active {
        background: linear-gradient(135deg, #00c896 0%, #00e5a0 100%);
        color: white;
    }
    
    .status-badge.completed {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .status-badge.upcoming {
        background: var(--bg-secondary);
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
    }
    </style>
""", unsafe_allow_html=True)

# Cache functions
@st.cache_resource
def init_connection():
    """Initialize Google Sheets connection"""
    gc = gspread.service_account(filename=CRED_PATH)
    return gc.open_by_url(SPREADSHEET_URL)

@st.cache_data(ttl=60)
def load_training_data():
    """Load all training data from Google Sheets"""
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
                    if row.get('Exercise') and str(row['Exercise']).strip() not in ['', 'Exercise']:
                        # Parse sets
                        sets_str = str(row.get('Sets', '0'))
                        if '-' in sets_str:
                            parts = sets_str.split('-')
                            sets = (float(parts[0]) + float(parts[1])) / 2 if len(parts) == 2 else 0
                        else:
                            try:
                                sets = float(sets_str) if sets_str else 0
                            except:
                                sets = 0
                        
                        # Parse reps
                        reps_str = str(row.get('Reps', '0'))
                        if '-' in reps_str:
                            parts = reps_str.split('-')
                            reps = (float(parts[0]) + float(parts[1])) / 2 if len(parts) == 2 else 0
                        else:
                            try:
                                reps = float(reps_str) if reps_str else 0
                            except:
                                reps = 0
                        
                        # Parse rest
                        rest_str = str(row.get('Rest (Seconds)', '0'))
                        try:
                            rest = float(rest_str) if rest_str else 0
                        except:
                            rest = 0
                        
                        all_data.append({
                            'Week': week_num,
                            'Day': row.get('Day', ''),
                            'Muscle Group': row.get('Muscle Group', ''),
                            'Exercise': row['Exercise'],
                            'Sets': sets,
                            'Reps': reps,
                            'Rest': rest,
                            'Volume': sets * reps
                        })
        except Exception as e:
            st.warning(f"Could not load Week {week_num}: {str(e)}")
            continue
    
    return pd.DataFrame(all_data)

def create_metric_card(icon, label, value, change=None, color="purple"):
    """Create a metric card with icon and optional change indicator"""
    change_html = ""
    if change is not None:
        direction = "↑" if change > 0 else "↓"
        change_class = "positive" if change > 0 else "negative"
        change_html = f'<div class="metric-change {change_class}">{direction} {abs(change):.1f}%</div>'
    
    return f"""
        <div class="metric-card">
            <div class="metric-icon {color}">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {change_html}
        </div>
    """

def create_progress_ring(percentage, label):
    """Create a circular progress indicator"""
    radius = 50
    stroke_width = 8
    circumference = 2 * np.pi * radius
    offset = circumference - (percentage / 100) * circumference
    
    return f"""
        <div class="progress-ring">
            <svg width="120" height="120">
                <circle cx="60" cy="60" r="{radius}" stroke="var(--bg-secondary)" 
                        stroke-width="{stroke_width}" fill="none"/>
                <circle cx="60" cy="60" r="{radius}" stroke="url(#gradient)" 
                        stroke-width="{stroke_width}" fill="none"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{offset}"
                        stroke-linecap="round"/>
                <defs>
                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                    </linearGradient>
                </defs>
            </svg>
            <div class="progress-value">{percentage}%</div>
        </div>
        <div style="text-align: center; margin-top: 1rem;">
            <div class="metric-label">{label}</div>
        </div>
    """

def main():
    # SIDEBAR (Data-Heavy Analytics)
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid var(--border-color); margin-bottom: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                <div style="font-family: 'Inter', sans-serif; font-weight: 700; font-size: 1.25rem; color: var(--text-primary);">
                    Training Analytics
                </div>
                <div style="font-family: 'Inter', sans-serif; font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                    Live Data Dashboard
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Load data
        try:
            df = load_training_data()
            if df.empty:
                st.error("❌ No training data found")
                st.info("Please ensure your Google Sheets has data in Week 1-8 sheets")
                st.stop()
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.stop()
        
        # Calculate current state
        current_week = df['Week'].max()
        available_weeks = sorted(df['Week'].unique())
        available_muscle_groups = sorted(df['Muscle Group'].unique())
        available_exercises = sorted(df['Exercise'].unique())
        
        st.markdown('<div class="sidebar-title">🎯 DATA FILTERS</div>', unsafe_allow_html=True)
        
        # Week filter
        selected_week = st.selectbox(
            "📅 Week Selection",
            options=["All Weeks"] + [f"Week {w}" for w in available_weeks],
            index=0
        )
        
        # Muscle group filter
        selected_muscle = st.selectbox(
            "💪 Muscle Group",
            options=["All Groups"] + available_muscle_groups,
            index=0
        )
        
        st.markdown('<div style="margin: 1.5rem 0; border-top: 1px solid var(--border-color);"></div>', unsafe_allow_html=True)
        
        # DETAILED STATS SECTION
        st.markdown('<div class="sidebar-title">📊 PERFORMANCE METRICS</div>', unsafe_allow_html=True)
        
        # Calculate detailed metrics
        total_workouts = len(df[df['Week'] <= current_week]['Day'].unique())
        total_exercises_done = len(df)
        avg_volume = df['Volume'].mean()
        total_volume = df['Volume'].sum()
        avg_sets_per_exercise = df['Sets'].mean()
        avg_reps_per_set = df['Reps'].mean()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Volume", f"{total_volume:,.0f}")
            st.metric("Exercises", f"{total_exercises_done}")
            st.metric("Avg Sets", f"{avg_sets_per_exercise:.1f}")
        
        with col2:
            st.metric("Workouts", f"{total_workouts}")
            st.metric("Avg Volume", f"{avg_volume:.0f}")
            st.metric("Avg Reps", f"{avg_reps_per_set:.1f}")
        
        st.markdown('<div style="margin: 1.5rem 0; border-top: 1px solid var(--border-color);"></div>', unsafe_allow_html=True)
        
        # WEEKLY BREAKDOWN
        st.markdown('<div class="sidebar-title">📈 WEEKLY BREAKDOWN</div>', unsafe_allow_html=True)
        
        weekly_stats = df.groupby('Week').agg({
            'Volume': 'sum',
            'Exercise': 'count',
            'Sets': 'sum'
        }).round(0)
        
        for week in weekly_stats.index:
            with st.expander(f"Week {week} Stats", expanded=bool(week == current_week)):
                st.markdown(f"""
                    <div style="font-family: 'Inter', sans-serif; font-size: 0.85rem; color: var(--text-secondary);">
                        <div style="display: flex; justify-content: space-between; margin: 0.25rem 0;">
                            <span>Volume:</span>
                            <span style="color: var(--text-primary); font-weight: 600;">{weekly_stats.loc[week, 'Volume']:.0f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 0.25rem 0;">
                            <span>Exercises:</span>
                            <span style="color: var(--text-primary); font-weight: 600;">{weekly_stats.loc[week, 'Exercise']:.0f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 0.25rem 0;">
                            <span>Total Sets:</span>
                            <span style="color: var(--text-primary); font-weight: 600;">{weekly_stats.loc[week, 'Sets']:.0f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<div style="margin: 1.5rem 0; border-top: 1px solid var(--border-color);"></div>', unsafe_allow_html=True)
        
        # TOP EXERCISES
        st.markdown('<div class="sidebar-title">🏆 TOP EXERCISES</div>', unsafe_allow_html=True)
        
        top_5_exercises = df.groupby('Exercise')['Volume'].sum().nlargest(5)
        for exercise, volume in top_5_exercises.items():
            progress_pct = (volume / top_5_exercises.iloc[0]) * 100
            st.markdown(f"""
                <div style="margin-bottom: 0.75rem;">
                    <div style="font-family: 'Inter', sans-serif; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">
                        {exercise}
                    </div>
                    <div style="background: var(--bg-primary); border-radius: 4px; height: 8px; position: relative;">
                        <div style="background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; width: {progress_pct}%; border-radius: 4px;"></div>
                    </div>
                    <div style="font-family: 'Inter', sans-serif; font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem; text-align: right;">
                        {volume:.0f} vol
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # MAIN CONTENT AREA
    # Apply filters
    filtered_df = df.copy()
    if selected_week != "All Weeks":
        week_num = int(selected_week.split()[1])
        filtered_df = filtered_df[filtered_df['Week'] == week_num]
    
    if selected_muscle != "All Groups":
        filtered_df = filtered_df[filtered_df['Muscle Group'] == selected_muscle]
    
    # Header with gradient
    st.markdown(f"""
        <div class="main-header">
            <div class="header-content">
                <div class="header-left">
                    <h1 class="app-title">ADAPTIVE TRAINING SYSTEM</h1>
                    <p class="app-subtitle">8-Week Progressive Overload Program • Intelligent Volume Management</p>
                </div>
                <div class="header-stats">
                    <div class="header-stat">
                        <div class="header-stat-value">{current_week}/8</div>
                        <div class="header-stat-label">Current Week</div>
                    </div>
                    <div class="header-stat">
                        <div class="header-stat-value">{len(filtered_df)}</div>
                        <div class="header-stat-label">Exercises</div>
                    </div>
                    <div class="header-stat">
                        <div class="header-stat-value">{filtered_df['Volume'].sum():.0f}</div>
                        <div class="header-stat-label">Total Volume</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Week Progress Bar
    st.markdown("""
        <div class="week-progress-container">
            <div class="week-progress-header">
                <div class="week-progress-title">PROGRAM PROGRESS</div>
                <div class="week-progress-value">Week {} of 8 • {:.0f}% Complete</div>
            </div>
            <div class="week-bars">
    """.format(current_week, (current_week/8)*100), unsafe_allow_html=True)
    
    for week in range(1, 9):
        if week < current_week:
            status = "completed"
            label = "✓"
        elif week == current_week:
            status = "current"
            label = f"W{week}"
        else:
            status = ""
            label = f"W{week}"
        
        st.markdown(f'<div class="week-bar {status}"><span class="week-bar-label">{label}</span></div>', unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Analytics", "📋 Training Log"])
    
    with tab1:
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate metrics
        total_volume = filtered_df['Volume'].sum()
        total_sets = filtered_df['Sets'].sum()
        avg_rest = filtered_df['Rest'].mean()
        unique_exercises = filtered_df['Exercise'].nunique()
        
        # Calculate week-over-week changes if possible
        if current_week > 1 and selected_week == "All Weeks":
            current_week_volume = df[df['Week'] == current_week]['Volume'].sum()
            prev_week_volume = df[df['Week'] == current_week - 1]['Volume'].sum()
            volume_change = ((current_week_volume - prev_week_volume) / prev_week_volume * 100) if prev_week_volume > 0 else 0
        else:
            volume_change = None
        
        with col1:
            st.markdown(create_metric_card("💪", "Total Volume", f"{total_volume:,.0f}", volume_change, "purple"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card("🎯", "Total Sets", f"{total_sets:,.0f}", None, "blue"), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card("⏱️", "Avg Rest", f"{avg_rest:.0f}s", None, "green"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card("📋", "Exercises", f"{unique_exercises}", None, "red"), unsafe_allow_html=True)
        
        # Charts Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-header"><div><div class="chart-title">WEEKLY VOLUME PROGRESSION</div><div class="chart-subtitle">Total training volume per week</div></div></div>', unsafe_allow_html=True)
            
            # Weekly volume chart
            weekly_volume = df.groupby('Week')['Volume'].sum().reset_index()
            
            fig = go.Figure()
            
            # Add gradient area chart
            fig.add_trace(go.Scatter(
                x=weekly_volume['Week'],
                y=weekly_volume['Volume'],
                mode='lines+markers',
                name='Volume',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8, color='#764ba2'),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)',
                hovertemplate='Week %{x}<br>Volume: %{y:,.0f}<extra></extra>'
            ))
            
            # Add current week indicator
            if current_week <= 8:
                fig.add_vline(
                    x=current_week,
                    line_dash="dash",
                    line_color="#00e5a0",
                    annotation_text=f"Current",
                    annotation_position="top"
                )
            
            fig.update_layout(
                plot_bgcolor='#1a1a28',
                paper_bgcolor='#1a1a28',
                font=dict(color='#a0a0b8', family='Inter'),
                xaxis=dict(
                    title='Week',
                    showgrid=True,
                    gridcolor='#2a2a3e',
                    zeroline=False
                ),
                yaxis=dict(
                    title='Volume',
                    showgrid=True,
                    gridcolor='#2a2a3e',
                    zeroline=False
                ),
                height=300,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-header"><div><div class="chart-title">MUSCLE GROUP DISTRIBUTION</div><div class="chart-subtitle">Volume by muscle group</div></div></div>', unsafe_allow_html=True)
            
            # Muscle group distribution
            muscle_dist = filtered_df.groupby('Muscle Group')['Volume'].sum().reset_index()
            muscle_dist = muscle_dist.sort_values('Volume', ascending=True)
            
            # Create gradient colors for each bar
            colors = ['#667eea', '#764ba2', '#00c896', '#00e5a0', '#ff4757', '#ff6b7a', '#4a9eff', '#667eea']
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=muscle_dist['Volume'],
                y=muscle_dist['Muscle Group'],
                orientation='h',
                marker=dict(
                    color=colors[:len(muscle_dist)],
                    line=dict(width=0)
                ),
                hovertemplate='%{y}<br>Volume: %{x:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                plot_bgcolor='#1a1a28',
                paper_bgcolor='#1a1a28',
                font=dict(color='#a0a0b8', family='Inter'),
                xaxis=dict(
                    title='Volume',
                    showgrid=True,
                    gridcolor='#2a2a3e',
                    zeroline=False
                ),
                yaxis=dict(
                    title='',
                    showgrid=False,
                    zeroline=False
                ),
                height=300,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Progress indicators row
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            progress_pct = (current_week / 8) * 100
            st.markdown(create_progress_ring(int(progress_pct), "PROGRAM COMPLETION"), unsafe_allow_html=True)
        
        with col2:
            # Calculate intensity (based on rest times - lower rest = higher intensity)
            avg_rest = filtered_df['Rest'].mean()
            intensity_pct = max(0, min(100, 100 - (avg_rest / 120 * 100)))  # Assuming 120s is low intensity
            st.markdown(create_progress_ring(int(intensity_pct), "TRAINING INTENSITY"), unsafe_allow_html=True)
        
        with col3:
            # Calculate consistency (how many planned exercises have data)
            consistency_pct = min(100, (len(filtered_df) / (unique_exercises * current_week)) * 100) if unique_exercises > 0 else 0
            st.markdown(create_progress_ring(int(consistency_pct), "CONSISTENCY SCORE"), unsafe_allow_html=True)
    
    with tab2:
        # Analytics view with more detailed charts
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-header"><div><div class="chart-title">EXERCISE VOLUME HEATMAP</div><div class="chart-subtitle">Volume distribution across weeks and muscle groups</div></div></div>', unsafe_allow_html=True)
        
        # Create heatmap data
        heatmap_data = df.pivot_table(
            values='Volume',
            index='Muscle Group',
            columns='Week',
            aggfunc='sum',
            fill_value=0
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=[f'Week {i}' for i in heatmap_data.columns],
            y=heatmap_data.index,
            colorscale=[
                [0, '#1a1a28'],
                [0.5, '#667eea'],
                [1, '#764ba2']
            ],
            hovertemplate='%{y}<br>%{x}<br>Volume: %{z:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            plot_bgcolor='#1a1a28',
            paper_bgcolor='#1a1a28',
            font=dict(color='#a0a0b8', family='Inter'),
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='', showgrid=False),
            height=400,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Exercise frequency chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-header"><div><div class="chart-title">TOP EXERCISES BY VOLUME</div><div class="chart-subtitle">Most demanding exercises</div></div></div>', unsafe_allow_html=True)
            
            top_exercises = filtered_df.groupby('Exercise')['Volume'].sum().nlargest(10).reset_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=top_exercises['Volume'],
                y=top_exercises['Exercise'],
                orientation='h',
                marker=dict(
                    color='#667eea',
                    line=dict(width=0)
                ),
                hovertemplate='%{y}<br>Volume: %{x:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                plot_bgcolor='#1a1a28',
                paper_bgcolor='#1a1a28',
                font=dict(color='#a0a0b8', family='Inter', size=10),
                xaxis=dict(showgrid=True, gridcolor='#2a2a3e'),
                yaxis=dict(showgrid=False),
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-header"><div><div class="chart-title">REST TIME DISTRIBUTION</div><div class="chart-subtitle">Recovery patterns</div></div></div>', unsafe_allow_html=True)
            
            # Rest time distribution
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=filtered_df['Rest'],
                nbinsx=20,
                marker=dict(
                    color='#00c896',
                    line=dict(width=0)
                ),
                hovertemplate='Rest: %{x}s<br>Count: %{y}<extra></extra>'
            ))
            
            fig.update_layout(
                plot_bgcolor='#1a1a28',
                paper_bgcolor='#1a1a28',
                font=dict(color='#a0a0b8', family='Inter'),
                xaxis=dict(title='Rest Time (seconds)', showgrid=True, gridcolor='#2a2a3e'),
                yaxis=dict(title='Frequency', showgrid=True, gridcolor='#2a2a3e'),
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:  # Training Log view
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-header"><div><div class="chart-title">TRAINING LOG</div><div class="chart-subtitle">Detailed exercise data</div></div></div>', unsafe_allow_html=True)
        
        # Format the dataframe for display
        display_df = filtered_df[['Week', 'Day', 'Muscle Group', 'Exercise', 'Sets', 'Reps', 'Rest', 'Volume']].copy()
        display_df['Sets'] = display_df['Sets'].apply(lambda x: f"{x:.0f}")
        display_df['Reps'] = display_df['Reps'].apply(lambda x: f"{x:.0f}")
        display_df['Rest'] = display_df['Rest'].apply(lambda x: f"{x:.0f}s")
        display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:.0f}")
        
        # Style the dataframe
        st.dataframe(
            display_df,
            use_container_width=True,
            height=500,
            hide_index=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown(f"""
                <div style="text-align: center;">
                    <div class="metric-label">TOTAL EXERCISES</div>
                    <div class="metric-value">{len(filtered_df)}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown(f"""
                <div style="text-align: center;">
                    <div class="metric-label">AVG SETS PER EXERCISE</div>
                    <div class="metric-value">{filtered_df['Sets'].mean():.1f}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown(f"""
                <div style="text-align: center;">
                    <div class="metric-label">AVG REPS PER SET</div>
                    <div class="metric-value">{filtered_df['Reps'].mean():.1f}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
