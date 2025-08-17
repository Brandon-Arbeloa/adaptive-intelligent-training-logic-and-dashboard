#!/usr/bin/env python3
"""
Training Dashboard - Similar to Grist version
Real-time connection to Google Sheets with all analytics
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

# Fix imports for Streamlit
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
    page_title="Intelligent Adaptive Training Dashboard",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Grist style with YOUR colors
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Clean Grist-like styling */
    .stApp {
        background: #f7f8f9;
    }
    
    /* Clean header like Grist */
    .main-header {
        background: white;
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 1.5rem -1rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0;
    }
    
    .main-subtitle {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 0.875rem;
        color: #666;
        margin-top: 0.25rem;
    }
    
    /* Metric cards - Grist style */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Tabs - Grist style */
    .stTabs [data-baseweb="tab-list"] {
        background: white;
        border-radius: 8px;
        padding: 0.25rem;
        gap: 0;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.875rem;
        border-radius: 6px;
        color: #666;
        background: transparent;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: #440052;
        color: white;
    }
    
    /* Week boxes - Grist style */
    .week-progress {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .week-box {
        flex: 1;
        height: 40px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s ease;
    }
    
    .week-complete {
        background: #008000;
        color: white;
    }
    
    .week-current {
        background: #440052;
        color: white;
        box-shadow: 0 0 0 2px #c40000;
    }
    
    .week-future {
        background: #f0f0f0;
        color: #999;
    }
    
    /* Sidebar - Grist style */
    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e0e0e0;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #1a1a1a;
    }
    
    section[data-testid="stSidebar"] h2 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.875rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    section[data-testid="stSidebar"] h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.875rem;
        color: #1a1a1a;
    }
    
    section[data-testid="stSidebar"] .stButton button {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        background: #440052;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        transition: all 0.2s ease;
    }
    
    section[data-testid="stSidebar"] .stButton button:hover {
        background: #040380;
    }
    
    /* Select boxes */
    .stMultiSelect > div > div {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
    }
    
    /* Clean chart backgrounds */
    .js-plotly-plot .plotly .bg {
        fill: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Cache the connection
@st.cache_resource
def init_connection():
    """Initialize Google Sheets connection"""
    gc = gspread.service_account(filename=CRED_PATH)
    return gc.open_by_url(SPREADSHEET_URL)

# Cache data with TTL
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
            
            if len(data) > 1:  # Has data beyond header
                df = pd.DataFrame(data[1:], columns=data[0])
                df['Week'] = week_num
                
                # Clean column names
                df.columns = df.columns.str.strip()
                
                # Store both raw and processed
                weeks_data[f"Week {week_num}"] = df
                
                # Process for analysis
                for _, row in df.iterrows():
                    if row.get('Exercise') and str(row['Exercise']).strip():
                        all_data.append({
                            'Week': week_num,
                            'Day': row.get('Day', ''),
                            'Muscle Group': row.get('Muscle Group', ''),
                            'Exercise': row['Exercise'],
                            'Sets': parse_number(row.get('Sets', 0)),
                            'Reps': parse_number(row.get('Reps', 0)),
                            'Rest': row.get('Rest (Seconds)', ''),
                            'RPE': parse_number(row.get('RPE', 0)),
                            'Volume': calculate_volume(row),
                            'Set 1': row.get('Set 1 (Weight - Reps)', ''),
                            'Set 2': row.get('Set 2 (Weight - Reps)', ''),
                            'Set 3': row.get('Set 3 (Weight - Reps)', ''),
                            'Set 4': row.get('Set 4 (Weight - Reps)', ''),
                        })
        except:
            pass
    
    # Load Performance Tracker if exists
    performance_data = None
    try:
        perf_sheet = ss.worksheet("Performance Tracker")
        perf_data = perf_sheet.get_all_values()
        if perf_data and len(perf_data) > 1:
            # Clean up column names - handle duplicates and empty columns
            headers = perf_data[0]
            cleaned_headers = []
            seen = {}
            
            for i, header in enumerate(headers):
                header = str(header).strip() if header else f"Column_{i+1}"
                
                # Handle duplicates
                if header in seen:
                    seen[header] += 1
                    header = f"{header}_{seen[header]}"
                else:
                    seen[header] = 0
                
                cleaned_headers.append(header)
            
            performance_data = pd.DataFrame(perf_data[1:], columns=cleaned_headers)
            
            # Remove columns that are all empty
            performance_data = performance_data.loc[:, (performance_data != '').any(axis=0)]
            
            # If DataFrame is empty after cleaning, set to None
            if performance_data.empty or len(performance_data.columns) == 0:
                performance_data = None
    except Exception as e:
        # Silent fail - performance data is optional
        performance_data = None
    
    # Load Exercise List
    exercise_list = {}
    try:
        ex_sheet = ss.worksheet("ExerciseList")
        ex_data = ex_sheet.get_all_values()
        for row in ex_data[1:]:
            if len(row) >= 2:
                muscle = row[0]
                exercise = row[1]
                if muscle not in exercise_list:
                    exercise_list[muscle] = []
                exercise_list[muscle].append(exercise)
    except:
        pass
    
    return pd.DataFrame(all_data), weeks_data, performance_data, exercise_list

def parse_number(value):
    """Parse numbers from various formats"""
    if not value:
        return 0
    
    value = str(value).strip()
    
    # Handle ranges
    if '-' in value:
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
    # Clean Grist-style header
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">Intelligent Adaptive Training Dashboard</h1>
            <p class="main-subtitle">Real-time Google Sheets Integration • Exercise Rotation Tracking</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load data
    try:
        with st.spinner('Loading training data...'):
            df, weeks_data, performance_data, exercise_list = load_all_data()
        
        if df.empty:
            st.warning("No training data found. Please add exercises to your Google Sheet.")
            st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Make sure your Google Sheet is properly configured and shared with the service account.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='font-size: 1rem; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;'>⚙️ Filters</h2>", unsafe_allow_html=True)
        
        # Get actual weeks with data
        weeks_with_data = sorted(df['Week'].unique())
        muscle_groups = sorted([mg for mg in df['Muscle Group'].unique() if mg])
        
        # Week selector
        selected_weeks = st.multiselect(
            "Select Weeks",
            options=list(range(1, 9)),
            default=weeks_with_data,
            key="week_selector"
        )
        
        # Muscle group filter
        selected_muscles = st.multiselect(
            "Muscle Groups",
            options=muscle_groups,
            default=muscle_groups,
            key="muscle_selector"
        )
        
        # Determine actual current week based on data
        # Current week = highest week with substantial data (>5 exercises)
        week_exercise_counts = df.groupby('Week')['Exercise'].count()
        weeks_with_substantial_data = week_exercise_counts[week_exercise_counts >= 5].index.tolist()
        
        if weeks_with_substantial_data:
            current_week = max(weeks_with_substantial_data)
        elif weeks_with_data:
            current_week = max(weeks_with_data)
        else:
            current_week = 1
        
        st.markdown("---")
        st.markdown("<h3 style='font-size: 1rem; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2rem;'>📊 Program Overview</h3>", unsafe_allow_html=True)
        
        # Week progress visual with accurate status
        week_html = '<div class="week-progress">'
        for week in range(1, 9):
            # Check if week has real data (not just placeholder rows)
            week_data = df[df['Week'] == week]
            has_real_data = len(week_data) >= 5  # At least 5 exercises to count as "real"
            
            if has_real_data:
                if week < current_week:
                    status = "week-complete"
                    label = "✓"
                elif week == current_week:
                    status = "week-current"
                    label = str(week)
                else:
                    status = "week-future"
                    label = str(week)
            else:
                status = "week-future"
                label = str(week)
            
            week_html += f'<div class="week-box {status}">{label}</div>'
        week_html += '</div>'
        
        st.markdown(week_html, unsafe_allow_html=True)
        
        # Quick stats
        st.markdown("<hr style='border: none; border-top: 1px solid #e0e0e0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Week", current_week)
        with col2:
            st.metric("Total Exercises", len(df))
        
        st.metric("Active Muscle Groups", len(selected_muscles))
        
        # Refresh button
        st.markdown("<hr style='border: none; border-top: 1px solid #e0e0e0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Filter data
    filtered_df = df[
        (df['Week'].isin(selected_weeks)) &
        (df['Muscle Group'].isin(selected_muscles))
    ]
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Progress Overview",
        "💪 Volume Analysis", 
        "🔄 Exercise Rotation",
        "📊 Performance Metrics",
        "🎯 Weekly Details",
        "📋 Raw Data"
    ])
    
    with tab1:
        st.markdown("### Training Progress Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_volume = filtered_df['Volume'].sum()
            st.metric("Total Volume", f"{total_volume:,.0f}")
        
        with col2:
            avg_rpe = filtered_df['RPE'].mean()
            st.metric("Average RPE", f"{avg_rpe:.1f}" if avg_rpe > 0 else "N/A")
        
        with col3:
            exercises_per_week = filtered_df.groupby('Week')['Exercise'].count().mean()
            st.metric("Avg Exercises/Week", f"{exercises_per_week:.0f}")
        
        with col4:
            unique_exercises = filtered_df['Exercise'].nunique()
            st.metric("Unique Exercises", unique_exercises)
        
        # Weekly progression chart
        weekly_stats = filtered_df.groupby('Week').agg({
            'Volume': 'sum',
            'Exercise': 'count',
            'Sets': 'mean',
            'Reps': 'mean'
        }).reset_index()
        
        # Clean Grist-style charts
        fig = go.Figure()
        
        # Bar chart with YOUR purple
        fig.add_trace(go.Bar(
            x=weekly_stats['Week'],
            y=weekly_stats['Volume'],
            name='Total Volume',
            marker_color='#440052',
            marker_line_color='#440052',
            marker_line_width=0
        ))
        
        # Line chart with YOUR red
        fig.add_trace(go.Scatter(
            x=weekly_stats['Week'],
            y=weekly_stats['Exercise'],
            name='Exercise Count',
            line=dict(color='#c40000', width=2),
            mode='lines+markers',
            marker=dict(size=6, color='#c40000'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title=None,
            xaxis_title="Week",
            yaxis=dict(title="Volume", side="left", showgrid=True, gridcolor='#f0f0f0'),
            yaxis2=dict(title="Exercise Count", overlaying="y", side="right", showgrid=False),
            hovermode='x unified',
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Inter", size=11, color="#666"),
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig.update_xaxes(showgrid=False, showline=True, linecolor='#e0e0e0')
        fig.update_yaxes(showline=True, linecolor='#e0e0e0')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Sets and Reps progression
        col1, col2 = st.columns(2)
        
        with col1:
            fig_sets = px.line(
                weekly_stats,
                x='Week',
                y='Sets',
                title="Average Sets Progression",
                markers=True
            )
            fig_sets.update_traces(line_color='#440052', mode='lines+markers', marker=dict(size=6))
            fig_sets.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Inter", size=11, color="#666"),
                title_font=dict(size=14, color="#1a1a1a"),
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            fig_sets.update_xaxes(showgrid=False, showline=True, linecolor='#e0e0e0')
            fig_sets.update_yaxes(showgrid=True, gridcolor='#f0f0f0', showline=True, linecolor='#e0e0e0')
            st.plotly_chart(fig_sets, use_container_width=True)
        
        with col2:
            fig_reps = px.line(
                weekly_stats,
                x='Week',
                y='Reps',
                title="Average Reps Progression",
                markers=True
            )
            fig_reps.update_traces(line_color='#040380', mode='lines+markers', marker=dict(size=6))
            fig_reps.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Inter", size=11, color="#666"),
                title_font=dict(size=14, color="#1a1a1a"),
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            fig_reps.update_xaxes(showgrid=False, showline=True, linecolor='#e0e0e0')
            fig_reps.update_yaxes(showgrid=True, gridcolor='#f0f0f0', showline=True, linecolor='#e0e0e0')
            st.plotly_chart(fig_reps, use_container_width=True)
    
    with tab2:
        st.markdown("### Volume Analysis by Muscle Group")
        
        # Volume by muscle group
        muscle_volume = filtered_df.groupby('Muscle Group')['Volume'].sum().reset_index()
        muscle_volume = muscle_volume.sort_values('Volume', ascending=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                muscle_volume,
                x='Volume',
                y='Muscle Group',
                orientation='h',
                title="Total Volume by Muscle Group",
                color='Volume',
                color_discrete_sequence=['#440052']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(
                muscle_volume,
                values='Volume',
                names='Muscle Group',
                title="Volume Distribution",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap
        st.markdown("### Weekly Volume Heatmap")
        
        heatmap_data = filtered_df.pivot_table(
            values='Volume',
            index='Muscle Group',
            columns='Week',
            aggfunc='sum',
            fill_value=0
        )
        
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Week", y="Muscle Group", color="Volume"),
            color_continuous_scale=[[0, 'white'], [1, '#440052']],
            aspect='auto',
            title="Volume Distribution Across Weeks"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Exercise Rotation Analysis")
        
        # Exercise frequency
        exercise_freq = filtered_df.groupby('Exercise').agg({
            'Week': lambda x: len(x.unique()),
            'Volume': 'sum',
            'Muscle Group': 'first'
        }).reset_index()
        
        exercise_freq.columns = ['Exercise', 'Weeks Used', 'Total Volume', 'Muscle Group']
        
        # Categorize by usage
        exercise_freq['Status'] = exercise_freq['Weeks Used'].apply(
            lambda x: '🔴 Overused' if x >= 4 else '🟡 Moderate' if x >= 2 else '🟢 Fresh'
        )
        
        # Rotation recommendations
        st.markdown("#### Rotation Status")
        
        col1, col2, col3 = st.columns(3)
        
        overused = exercise_freq[exercise_freq['Status'] == '🔴 Overused']
        moderate = exercise_freq[exercise_freq['Status'] == '🟡 Moderate']
        fresh = exercise_freq[exercise_freq['Status'] == '🟢 Fresh']
        
        with col1:
            st.metric("Overused (4+ weeks)", len(overused))
            if not overused.empty:
                st.dataframe(
                    overused[['Exercise', 'Weeks Used']].head(5),
                    hide_index=True
                )
        
        with col2:
            st.metric("Moderate (2-3 weeks)", len(moderate))
            if not moderate.empty:
                st.dataframe(
                    moderate[['Exercise', 'Weeks Used']].head(5),
                    hide_index=True
                )
        
        with col3:
            st.metric("Fresh (<2 weeks)", len(fresh))
            if not fresh.empty:
                st.dataframe(
                    fresh[['Exercise', 'Weeks Used']].head(5),
                    hide_index=True
                )
        
        # Exercise frequency chart
        st.markdown("#### Top Exercises by Frequency")
        
        top_exercises = exercise_freq.nlargest(15, 'Weeks Used')
        
        fig = px.bar(
            top_exercises,
            x='Weeks Used',
            y='Exercise',
            orientation='h',
            color='Status',
            color_discrete_map={
                '🔴 Overused': '#c40000',
                '🟡 Moderate': '#040380',
                '🟢 Fresh': '#008000'
            },
            title="Exercise Usage Across Weeks"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### Performance Metrics")
        
        if performance_data is not None and not performance_data.empty:
            # Display performance data
            st.dataframe(performance_data, use_container_width=True)
        else:
            # Calculate performance metrics from training data
            st.markdown("#### Calculated Performance Indicators")
            
            # Progressive overload tracking
            exercise_progression = []
            
            for exercise in filtered_df['Exercise'].unique():
                ex_data = filtered_df[filtered_df['Exercise'] == exercise]
                if len(ex_data) > 1:
                    weeks = sorted(ex_data['Week'].unique())
                    if len(weeks) > 1:
                        first_week_vol = ex_data[ex_data['Week'] == weeks[0]]['Volume'].mean()
                        last_week_vol = ex_data[ex_data['Week'] == weeks[-1]]['Volume'].mean()
                        
                        if first_week_vol > 0:
                            progress = ((last_week_vol - first_week_vol) / first_week_vol) * 100
                            exercise_progression.append({
                                'Exercise': exercise,
                                'First Week': weeks[0],
                                'Last Week': weeks[-1],
                                'Progress %': progress
                            })
            
            if exercise_progression:
                prog_df = pd.DataFrame(exercise_progression)
                prog_df = prog_df.sort_values('Progress %', ascending=False)
                
                # Top gainers and losers
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 📈 Top Progressions")
                    st.dataframe(
                        prog_df.head(5).style.format({'Progress %': '{:.1f}%'}),
                        hide_index=True
                    )
                
                with col2:
                    st.markdown("##### 📉 Needs Attention")
                    st.dataframe(
                        prog_df.tail(5).style.format({'Progress %': '{:.1f}%'}),
                        hide_index=True
                    )
    
    with tab5:
        st.markdown("### Weekly Training Details")
        
        selected_week = st.selectbox(
            "Select Week",
            options=selected_weeks,
            index=len(selected_weeks)-1 if selected_weeks else 0
        )
        
        week_key = f"Week {selected_week}"
        if week_key in weeks_data:
            week_df = weeks_data[week_key]
            
            # Summary metrics for the week
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                exercises = len([e for e in week_df['Exercise'] if e and str(e).strip()])
                st.metric("Exercises", exercises)
            
            with col2:
                days = len([d for d in week_df['Day'].unique() if d and str(d).strip()])
                st.metric("Training Days", days)
            
            with col3:
                muscle_count = len([m for m in week_df['Muscle Group'].unique() if m and str(m).strip()])
                st.metric("Muscle Groups", muscle_count)
            
            with col4:
                # Calculate average sets
                sets_vals = [parse_number(s) for s in week_df['Sets'] if s]
                avg_sets = np.mean(sets_vals) if sets_vals else 0
                st.metric("Avg Sets", f"{avg_sets:.1f}")
            
            # Display the week's data
            st.dataframe(
                week_df[['Day', 'Muscle Group', 'Exercise', 'Sets', 'Reps', 'Rest (Seconds)', 'RPE']],
                use_container_width=True,
                hide_index=True
            )
    
    with tab6:
        st.markdown("### Raw Training Data")
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"training_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Display raw data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Summary statistics
        st.markdown("### Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Volume Stats**")
            st.write(f"Total: {filtered_df['Volume'].sum():,.0f}")
            st.write(f"Average: {filtered_df['Volume'].mean():,.1f}")
            st.write(f"Max: {filtered_df['Volume'].max():,.0f}")
        
        with col2:
            st.markdown("**Sets/Reps Stats**")
            st.write(f"Avg Sets: {filtered_df['Sets'].mean():.1f}")
            st.write(f"Avg Reps: {filtered_df['Reps'].mean():.1f}")
            st.write(f"Total Sets: {filtered_df['Sets'].sum():.0f}")
        
        with col3:
            st.markdown("**Exercise Stats**")
            st.write(f"Unique Exercises: {filtered_df['Exercise'].nunique()}")
            st.write(f"Total Exercises: {len(filtered_df)}")
            st.write(f"Exercises/Week: {len(filtered_df)/len(selected_weeks):.1f}")

if __name__ == "__main__":
    main()