import streamlit as st
import pandas as pd
import json
import base64
import logging
from github import Github

# ---- Streamlit Page Config ----
st.set_page_config(page_title="Global WRVSL Survey", layout="wide")

# ---- Define Survey Sections ----
SECTIONS = [
    "Participant Context",
    "System Design",
    "Operational Challenges",
    "Impact Assessment",
    "Lessons Learned",
    "Policy & Governance",
    "Future Directions",
    "Optional Demographics"
]

# ---- Initialize Session State ----
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# ---- Sidebar Navigation ----
st.sidebar.title("📋 Survey Progress")
progress = (st.session_state.current_section + 1) / len(SECTIONS)
st.sidebar.progress(progress, text=f"{int(progress*100)}% Complete")

for i, section in enumerate(SECTIONS):
    if i == st.session_state.current_section:
        st.sidebar.markdown(f"➡️ **{section}**")
    else:
        if st.sidebar.button(section):
            st.session_state.current_section = i
            st.rerun()

# ---- Function to Render Sections ----
def show_section(section_num):
    """Renders the current survey section with tooltips for better clarity."""
    st.subheader(f"📝 {SECTIONS[section_num]}")

    if section_num == 0:  # Participant Context
        st.session_state.responses['region'] = st.radio(
            "**1. Geographical region of operation**", 
            ['North America', 'Europe', 'Australia/NZ', 'Asia', 'Middle East', 'Africa', 'South America'],
            help="Select the primary region where your WRVSL system is deployed."
        )
        st.session_state.responses['experience'] = st.radio(
            "**2. Years of experience with WRVSL systems**", 
            ['<1 year', '1–3 years', '4–7 years', '8+ years'],
            help="How long have you been involved with WRVSL systems?"
        )
        st.session_state.responses['org_type'] = st.selectbox(
            "**3. Organization type**", 
            ['Government agency', 'Private consultancy', 'Academic', 'NGO', 'Other'],
            help="Select the type of organization you work for."
        )

    elif section_num == 1:  # System Design
        vsl_selection = st.multiselect(
            "**4. Types of VSL systems managed**", 
            ['Congestion-responsive', 'Weather-responsive', 'Event-specific', 'Other'],
            help="Select all types of VSL systems you manage."
        )
        st.session_state.responses['vsl_types'] = vsl_selection
        if 'Other' in vsl_selection:
            st.session_state.responses['vsl_other'] = st.text_input(
                "Specify other VSL type",
                help="If you selected 'Other', please describe the type of VSL system."
            )

        st.session_state.responses['weather_params'] = st.multiselect(
            "**5. Weather parameter(s) triggering speed adjustments**", 
            ['Rainfall intensity', 'Snow accumulation', 'Pavement friction', 'Visibility', 'Wind speed', 'Other'],
            help="Select weather conditions that trigger speed adjustments in your system."
        )

        st.session_state.responses['control_logic'] = st.radio(
            "**8. Control logic architecture**", 
            ['Rule-based thresholds (fixed)', 'Dynamic thresholds (real-time adjustments)', 'Machine learning based'],
            help="Select how your WRVSL system determines speed limit changes."
        )

    # Other sections follow the same pattern, ensuring clarity with tooltips

# ---- Call Function to Render Section ----
show_section(st.session_state.current_section)

# ---- Save Responses to GitHub ----
def save_to_github(df):
    """Saves responses to GitHub without overwriting previous data."""
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("abdhulkhadhir/WISE_Questionnaire")
        file_path = "responses.csv"

        # Load existing file content
        try:
            file = repo.get_contents(file_path)
            existing_data = pd.read_csv(file.download_url)
        except:
            existing_data = pd.DataFrame()

        # Append new response
        updated_data = pd.concat([existing_data, df], ignore_index=True)
        file_content = updated_data.to_csv(index=False)

        # Commit update
        if 'file' in locals():
            repo.update_file(file_path, "Update WRVSL responses", file_content, file.sha)
        else:
            repo.create_file(file_path, "Create WRVSL responses", file_content)
        
        st.success("Responses saved successfully!")

    except Exception as e:
        logging.error(f"Error saving to GitHub: {e}")
        st.error("Error saving responses. Please try again.")

# ---- Navigation Buttons ----
col1, col2 = st.columns([1, 1])
with col1:
    if st.session_state.current_section > 0:
        if st.button("⬅️ Previous"):
            st.session_state.current_section -= 1
            st.rerun()

with col2:
    if st.session_state.current_section < len(SECTIONS) - 1:
        if st.button("Next ➡️"):
            st.session_state.current_section += 1
            st.rerun()
    else:
        if st.button("✅ Submit"):
            df = pd.DataFrame([st.session_state.responses])
            save_to_github(df)
            st.session_state.submitted = True
