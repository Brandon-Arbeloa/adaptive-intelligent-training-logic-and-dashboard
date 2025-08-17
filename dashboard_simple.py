#!/usr/bin/env python3
"""
Training Dashboard - Clean Grist Style
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
    page_title="Training Dashboard",
    page_icon="💪",
    layout="wide"
)

# Initialize connection
@st.cache_resource
def init_connection():
    gc = gspread.service_account(filename=CRED_PATH)
    return gc.open_by_url(SPREADSHEET_URL)

# Load data
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
                        # Parse numbers safely
                        sets = row.get('Sets', '0')
                        reps = row.get('Reps', '0')
                        
                        # Handle ranges
                        if '-' in str(sets):
                            parts = str(sets).split('-')
                            sets_val = (float(parts[0]) + float(parts[1])) / 2 if len(parts) == 2 else float(parts[0])
                        else:
                            try:
                                sets_val = float(sets)
                            except:
                                sets_val = 0
                        
                        if '-' in str(reps):
                            parts = str(reps).split('-')
                            reps_val = (float(parts[0]) + float(parts[1])) / 2 if len(parts) == 2 else float(parts[0])
                        else:
                            try:
                                reps_val = float(reps)
                            except:
                                reps_val = 0
                        
                        all_data.append({
                            'Week': week_num,
                            'Muscle Group': row.get('Muscle Group', ''),
                            'Exercise': row['Exercise'],
                            'Sets': sets_val,
                            'Reps': reps_val,
                            'Volume': sets_val * reps_val
                        })
        except:
            pass
    
    return pd.DataFrame(all_data)

# Main app
def main():
    # Title
    st.title("Training Dashboard")
    st.caption("Real-time sync with Google Sheets")
    
    # Load data
    try:
        df = load_data()
        if df.empty:
            st.error("No training data found")
            st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        weeks_available = sorted(df['Week'].unique())
        selected_weeks = st.multiselect(
            "Weeks",
            options=weeks_available,
            default=weeks_available
        )
        
        muscles_available = sorted(df['Muscle Group'].unique())
        selected_muscles = st.multiselect(
            "Muscle Groups",
            options=muscles_available,
            default=muscles_available
        )
        
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Filter data
    filtered_df = df[
        (df['Week'].isin(selected_weeks)) & 
        (df['Muscle Group'].isin(selected_muscles))
    ]
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Volume", f"{filtered_df['Volume'].sum():,.0f}")
    with col2:
        st.metric("Exercises", len(filtered_df))
    with col3:
        st.metric("Avg Sets", f"{filtered_df['Sets'].mean():.1f}")
    with col4:
        st.metric("Avg Reps", f"{filtered_df['Reps'].mean():.1f}")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Weekly Progress", "Muscle Groups", "Exercise Rotation"])
    
    with tab1:
        # Weekly volume chart
        weekly = filtered_df.groupby('Week').agg({
            'Volume': 'sum',
            'Exercise': 'count'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=weekly['Week'],
            y=weekly['Volume'],
            name='Volume',
            marker_color='#440052'
        ))
        
        fig.update_layout(
            title="Weekly Volume",
            xaxis_title="Week",
            yaxis_title="Total Volume",
            height=400,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Muscle group distribution
        muscle_vol = filtered_df.groupby('Muscle Group')['Volume'].sum().reset_index()
        muscle_vol = muscle_vol.sort_values('Volume', ascending=False)
        
        fig = px.bar(
            muscle_vol,
            x='Muscle Group',
            y='Volume',
            title="Volume by Muscle Group",
            color_discrete_sequence=['#040380']
        )
        
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Exercise frequency
        exercise_freq = filtered_df.groupby('Exercise')['Week'].nunique().reset_index()
        exercise_freq.columns = ['Exercise', 'Weeks Used']
        exercise_freq = exercise_freq.sort_values('Weeks Used', ascending=False)
        
        # Show top 10
        st.subheader("Exercise Frequency")
        
        for _, row in exercise_freq.head(10).iterrows():
            weeks = row['Weeks Used']
            if weeks >= 4:
                color = "🔴"
                status = "Overused"
            elif weeks >= 2:
                color = "🟡"
                status = "Good"
            else:
                color = "🟢"
                status = "Fresh"
            
            st.write(f"{color} **{row['Exercise']}** - {weeks} weeks ({status})")

if __name__ == "__main__":
    main()