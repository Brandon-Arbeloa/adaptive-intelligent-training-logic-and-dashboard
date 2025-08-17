#!/usr/bin/env python3
"""
Training Dashboard - Clean, Professional Design
Real-time connection to Google Sheets
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
from pathlib import Path
import sys

# Fix imports
import os
from pathlib import Path

# Set up paths
BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / 'backend'

# Add backend to path
import sys
sys.path.insert(0, str(BACKEND_DIR))

# Now import from backend
try:
    from config import CRED_PATH, SPREADSHEET_URL
except ImportError:
    # Fallback to direct values
    CRED_PATH = str(BASE_DIR / 'credentials.json')
    SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1Js2s7s95miuUzdn44guWnGuML2kxYzN3kG_jsEdWu68/edit'

# Page config
st.set_page_config(
    page_title="Training Dashboard",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, minimal CSS
st.markdown("""
    <style>
    /* Clean, professional design */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
    
    .stApp {
        background: #ffffff;
    }
    
    /* Header */
    .main-header {
        background: #000000;
        color: white;
        padding: 2rem 3rem;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .main-subtitle {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1rem;
        color: #999999;
        margin-top: 0.5rem;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 1.5rem;
        border-radius: 8px;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        color: #000000;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        gap: 2rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        color: #666666;
        background: transparent;
        border: none;
        padding-bottom: 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        color: #000000;
        border-bottom: 3px solid #000000;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    section[data-testid="stSidebar"] h2 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 1rem;
        color: #000000;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    section[data-testid="stSidebar"] .stButton button {
        background: #000000;
        color: white;
        border: none;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    section[data-testid="stSidebar"] .stButton button:hover {
        background: #333333;
    }
    
    /* Week boxes */
    .week-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
        margin: 1.5rem 0;
    }
    
    .week-box {
        padding: 1rem;
        text-align: center;
        border-radius: 4px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .week-complete {
        background: #000000;
        color: white;
    }
    
    .week-current {
        background: #ffffff;
        color: #000000;
        border: 2px solid #000000;
        font-weight: 800;
    }
    
    .week-future {
        background: #f0f0f0;
        color: #999999;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Cache functions
@st.cache_resource
def init_connection():
    """Initialize Google Sheets connection"""
    gc = gspread.service_account(filename=CRED_PATH)
    return gc.open_by_url(SPREADSHEET_URL)

@st.cache_data(ttl=60)
def load_all_data():
    """Load all training data from Google Sheets"""
    ss = init_connection()
    
    all_data = []
    weeks_data = {}
    
    # Load each week
    for week_num in range(1, 9):
        try:
            sheet = ss.worksheet(f"Week {week_num}")
            data = sheet.get_all_values()
            
            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
                df['Week'] = week_num
                
                # Clean column names
                df.columns = df.columns.str.strip()
                
                weeks_data[f"Week {week_num}"] = df
                
                # Process for analysis
                for _, row in df.iterrows():
                    if row.get('Exercise') and str(row['Exercise']).strip() and row['Exercise'] != 'Exercise':
                        all_data.append({
                            'Week': week_num,
                            'Day': row.get('Day', ''),
                            'Muscle Group': row.get('Muscle Group', ''),
                            'Exercise': row['Exercise'],
                            'Sets': parse_number(row.get('Sets', 0)),
                            'Reps': parse_number(row.get('Reps', 0)),
                            'Rest': row.get('Rest (Seconds)', ''),
                            'Volume': calculate_volume(row)
                        })
        except:
            pass
    
    return pd.DataFrame(all_data), weeks_data

def parse_number(value):
    """Parse numbers from various formats"""
    if not value:
        return 0
    
    value = str(value).strip()
    
    # Handle ranges
    if '-' in value and not value.startswith('-'):
        parts = value.split('-')
        try:
            return (float(parts[0]) + float(parts[1])) / 2
        except:
            return 0
    
    try:
        return float(value)
    except:
        return 0

def calculate_volume(row):
    """Calculate volume from sets and reps"""
    sets = parse_number(row.get('Sets', 0))
    reps = parse_number(row.get('Reps', 0))
    return sets * reps

def main():
    # Clean header
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">Training Dashboard</h1>
            <p class="main-subtitle">Intelligent Adaptive Training System</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load data
    try:
        with st.spinner('Loading...'):
            df, weeks_data = load_all_data()
        
        if df.empty:
            st.warning("No training data found in Google Sheets")
            st.stop()
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## Filters")
        
        # Get weeks with real data
        weeks_with_data = sorted(df['Week'].unique())
        
        selected_weeks = st.multiselect(
            "Weeks",
            options=list(range(1, 9)),
            default=weeks_with_data
        )
        
        muscle_groups = sorted([mg for mg in df['Muscle Group'].unique() if mg])
        selected_muscles = st.multiselect(
            "Muscle Groups",
            options=muscle_groups,
            default=muscle_groups
        )
        
        # Current week detection
        week_counts = df.groupby('Week')['Exercise'].count()
        current_week = week_counts[week_counts >= 5].index.max() if not week_counts.empty else 1
        
        st.markdown("---")
        st.markdown("## Progress")
        
        # Week grid
        week_html = '<div class="week-grid">'
        for week in range(1, 9):
            week_data = df[df['Week'] == week]
            has_data = len(week_data) >= 5
            
            if has_data and week < current_week:
                status = "week-complete"
                label = f"Week {week} ✓"
            elif has_data and week == current_week:
                status = "week-current"
                label = f"Week {week}"
            else:
                status = "week-future"
                label = f"Week {week}"
            
            week_html += f'<div class="week-box {status}">{label}</div>'
        week_html += '</div>'
        
        st.markdown(week_html, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Week", current_week)
        with col2:
            st.metric("Total Exercises", len(df))
        
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Filter data
    filtered_df = df[
        (df['Week'].isin(selected_weeks)) &
        (df['Muscle Group'].isin(selected_muscles))
    ]
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview",
        "Volume Analysis",
        "Exercise Rotation",
        "Raw Data"
    ])
    
    with tab1:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Volume", f"{filtered_df['Volume'].sum():,.0f}")
        
        with col2:
            st.metric("Avg Sets", f"{filtered_df['Sets'].mean():.1f}")
        
        with col3:
            st.metric("Avg Reps", f"{filtered_df['Reps'].mean():.1f}")
        
        with col4:
            st.metric("Unique Exercises", filtered_df['Exercise'].nunique())
        
        # Weekly progression
        st.markdown("### Weekly Progression")
        
        weekly_stats = filtered_df.groupby('Week').agg({
            'Volume': 'sum',
            'Exercise': 'count'
        }).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=weekly_stats['Week'],
            y=weekly_stats['Volume'],
            name='Volume',
            marker_color='#000000'
        ))
        
        fig.update_layout(
            xaxis_title="Week",
            yaxis_title="Total Volume",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Inter", color="#000000"),
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Volume by Muscle Group")
        
        muscle_volume = filtered_df.groupby('Muscle Group')['Volume'].sum().reset_index()
        muscle_volume = muscle_volume.sort_values('Volume', ascending=False)
        
        fig = px.bar(
            muscle_volume,
            x='Muscle Group',
            y='Volume',
            color_discrete_sequence=['#000000']
        )
        
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Total Volume",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Inter", color="#000000"),
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume heatmap
        st.markdown("### Weekly Distribution")
        
        pivot_data = filtered_df.pivot_table(
            values='Volume',
            index='Muscle Group',
            columns='Week',
            aggfunc='sum',
            fill_value=0
        )
        
        fig = px.imshow(
            pivot_data,
            color_continuous_scale=['white', '#000000'],
            aspect='auto'
        )
        
        fig.update_layout(
            font=dict(family="Inter", color="#000000")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Exercise Frequency")
        
        exercise_freq = filtered_df.groupby('Exercise')['Week'].nunique().reset_index()
        exercise_freq.columns = ['Exercise', 'Weeks Used']
        exercise_freq = exercise_freq.sort_values('Weeks Used', ascending=False)
        
        # Categories
        overused = exercise_freq[exercise_freq['Weeks Used'] >= 4]
        optimal = exercise_freq[(exercise_freq['Weeks Used'] >= 2) & (exercise_freq['Weeks Used'] < 4)]
        underused = exercise_freq[exercise_freq['Weeks Used'] < 2]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### ⚠️ Overused (4+ weeks)")
            if not overused.empty:
                for _, row in overused.head(10).iterrows():
                    st.write(f"• {row['Exercise']} ({row['Weeks Used']} weeks)")
            else:
                st.write("None")
        
        with col2:
            st.markdown("#### ✓ Optimal (2-3 weeks)")
            if not optimal.empty:
                for _, row in optimal.head(10).iterrows():
                    st.write(f"• {row['Exercise']} ({row['Weeks Used']} weeks)")
            else:
                st.write("None")
        
        with col3:
            st.markdown("#### 💡 Fresh (<2 weeks)")
            if not underused.empty:
                for _, row in underused.head(10).iterrows():
                    st.write(f"• {row['Exercise']} ({row['Weeks Used']} week)")
            else:
                st.write("None")
    
    with tab4:
        st.markdown("### Training Data")
        
        # Download
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"training_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Display
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    main()