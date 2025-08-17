#!/usr/bin/env python3
"""
Premium Training Dashboard - Professional SaaS-Quality Design
Works both locally and on Streamlit Cloud
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
import json
import os

# Fix imports
BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

# Handle credentials for both local and Streamlit Cloud
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1Js2s7s95miuUzdn44guWnGuML2kxYzN3kG_jsEdWu68/edit'

def get_credentials():
    """Get credentials from either local file or Streamlit secrets"""
    # Try Streamlit Cloud secrets first
    try:
        if 'gcp_service_account' in st.secrets:
            # Convert Streamlit secrets to proper dict format
            creds = dict(st.secrets['gcp_service_account'])
            
            # Fix the private key newlines (common issue with TOML secrets)
            if 'private_key' in creds:
                creds['private_key'] = creds['private_key'].replace('\\n', '\n')
                
            return creds
    except Exception as e:
        st.error(f"Error loading Streamlit secrets: {str(e)}")
        pass
    
    # Fall back to local credentials.json
    cred_path = BASE_DIR / 'credentials.json'
    if cred_path.exists():
        with open(cred_path, 'r') as f:
            return json.load(f)
    
    st.error("No credentials found! Please add credentials.json locally or configure Streamlit Cloud secrets.")
    st.stop()

# Initialize connection with flexible credentials
@st.cache_resource
def init_connection():
    """Initialize Google Sheets connection"""
    creds = get_credentials()
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_url(SPREADSHEET_URL)
