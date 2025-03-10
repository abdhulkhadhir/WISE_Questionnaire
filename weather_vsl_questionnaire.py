# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 12:23:30 2025

@author: seyedhyd
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import base64
from github import Github
import os

# Initialize session state
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Configure GitHub integration
if "GITHUB_TOKEN" not in st.secrets:
    st.error("GitHub token is missing. Please configure `st.secrets`.")
    st.stop()

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "abdhulkhadhir/qd_visualiser"
CSV_PATH = "responses.csv"

# Section configurations
SECTIONS = [
    "Participant Context",
    "System Design",
    "Operational Challenges",
    "Impact Assessment",
    "Lessons Learned",
    "Policy & Governance",
    "Future Directions",
    "Demographics"
]

# Progress bar
progress = st.session_state.current_section / (len(SECTIONS)-1)

# Tooltips
TOOLTIPS = {
    "control_logic": "Control logic refers to the algorithmic approach used to determine speed limits",
    "rwis": "Road Weather Information System (RWIS) uses roadside sensors to monitor conditions",
    "mucd": "Manual on Uniform Traffic Control Devices (MUTCD) - US regulatory framework"
}

def show_section(section_num):
    st.markdown(f"## {SECTIONS[section_num]}")
    
    if section_num == 0:  # Participant Context
        with st.expander("**About This Survey**"):
            st.markdown("""
            This survey collects global insights on weather-responsive VSL systems. 
            All responses are anonymized and will be used for academic research.
            """)
            
        cols = st.columns(2)
        with cols[0]:
            st.session_state.responses['region'] = st.radio(
                "**1. Geographical region of operation**",
                options=['North America', 'Europe', 'Australia/NZ', 'Asia', 
                        'Middle East', 'Africa', 'South America']
            )
        with cols[1]:
            st.session_state.responses['experience'] = st.radio(
                "**2. Years of experience with WRVSL systems**",
                options=['<1 year', '1–3 years', '4–7 years', '8+ years']
            )
            
        st.session_state.responses['org_type'] = st.selectbox(
            "**3. Organization type**",
            options=['Government agency', 'Private consultancy', 
                    'Academic', 'NGO', 'Other']
        )

    elif section_num == 1:  # System Design
        cols = st.columns(2)
        with cols[0]:
            st.markdown("### System Configuration")
            st.session_state.responses['vsl_types'] = st.multiselect(
                "**4. Types of VSL systems managed**",
                options=['Congestion-responsive', 'Weather-responsive', 
                        'Event-specific', 'Other']
            )
            
            weather_params = st.multiselect(
                "**5. Primary weather parameters triggering adjustments**",
                options=['Rainfall intensity', 'Snow accumulation', 'Pavement friction',
                        'Visibility', 'Wind speed', 'Humidity', 'Other']
            )
            st.session_state.responses['weather_params'] = ", ".join(weather_params) if weather_params else "None"
            
        with cols[1]:
            st.markdown("### Data & Control Logic")
            data_sources = ["RWIS/roadside sensors", "Connected vehicle telematics",
                           "Radar/satellite forecasts", "Thermal cameras",
                           "Manual operator reports"]
            ranked = st.multiselect(
                "**6. Rank data sources (1=Most Critical)**",
                options=data_sources,
                default=data_sources,
                format_func=lambda x: f"{data_sources.index(x)+1}. {x}"
            )
            st.session_state.responses['data_sources'] = ", ".join(ranked) if ranked else "None"
            
            control_logic = st.radio(
                "**7. Control logic architecture**",
                options=['Rule-based thresholds (fixed)', 
                        'Dynamic thresholds (real-time adjustments)',
                        'Machine learning based'],
                help=TOOLTIPS['control_logic']
            )
            st.session_state.responses['control_logic'] = control_logic
            
            if "Rule-based" in control_logic:
                threshold_method = st.radio(
                    "**How were thresholds determined?**",
                    options=['Historical crash data', 'Regulatory guidelines',
                            'Trial-and-error', 'Other']
                )
                st.session_state.responses['threshold_method'] = threshold_method

def save_to_github(df):
    """Save responses to GitHub repo"""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)

        # Check if file exists
        try:
            contents = repo.get_contents(CSV_PATH)
            existing_data = pd.read_csv(contents.decoded_content.decode("utf-8"))
            updated_df = pd.concat([existing_data, df])
            repo.update_file(contents.path, "Update VSL responses", updated_df.to_csv(index=False), contents.sha)
        except Exception:
            # File does not exist, create a new one
            repo.create_file(CSV_PATH, "Create VSL responses", df.to_csv(index=False))
        
        return True
    except Exception as e:
        st.error(f"GitHub save error: {e}")
        return False

# Main app layout
st.set_page_config(page_title="Global VSL Survey", layout="wide")
st.markdown("""
<style>
    [data-testid=stSidebar] {
        display: none !important;
    }
    .stProgress > div > div > div {
        background-color: #1E90FF;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌦️ Global Weather-Responsive VSL Survey")
st.markdown(f"**Progress:** {int(progress*100)}% complete")
st.progress(progress)

# Show current section
show_section(st.session_state.current_section)

# Navigation controls
col1, col2, col3 = st.columns([2,1,2])
with col2:
    if st.session_state.current_section > 0:
        if st.button("← Previous Section"):
            st.session_state.current_section -= 1
            st.experimental_rerun()
            
    if st.session_state.current_section < len(SECTIONS)-1:
        if st.button("Next Section →"):
            # Add validation here
            st.session_state.current_section += 1
            st.experimental_rerun()
    else:
        if st.button("Submit Responses"):
            df = pd.DataFrame([st.session_state.responses])
            
            # Save to GitHub
            if GITHUB_TOKEN:
                if save_to_github(df):
                    st.success("Responses saved successfully!")
                else:
                    st.error("Error saving responses")
            
            # Local download fallback
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Responses",
                data=csv,
                file_name='vsl_responses.csv',
                mime='text/csv'
            )
            
            # Properly reset session state after submission
            st.session_state.responses = {}
            st.session_state.current_section = 0
            st.session_state.submitted = True
            st.experimental_rerun()
