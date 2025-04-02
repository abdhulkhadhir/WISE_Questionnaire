import streamlit as st
import pandas as pd
import json
import base64
import logging
from github import Github
from io import StringIO

# ---- Streamlit Page Config ----
st.set_page_config(page_title="Global WRVSL State of Practice Survey", layout="wide")

# ---- Custom CSS for Better Styling ----
st.markdown("""
    <style>
        .main-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# ---- GitHub Configuration ----
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "abdhulkhadhir/WISE_Questionnaire"
CSV_PATH = "responses.csv"

# ---- Survey Sections ----
SECTIONS = [
    "Home", "Participant Context", "System Design", "Operational Challenges", "Impact Assessment",
    "Lessons Learned", "Policy & Governance", "Future Directions", "Optional Demographics"
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
st.sidebar.progress(progress)

section_choice = st.sidebar.radio("Navigate to:", SECTIONS, index=st.session_state.current_section)
st.session_state.current_section = SECTIONS.index(section_choice)

# ---- Function to Render Sections ----
def show_section(section_num):
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    if section_num == 0:
        st.image("header_image.jpg", use_column_width=True)
        st.markdown("""
            # Welcome to the Global WRVSL Survey! 🎉
            **Why this survey?**  
            Your insights will help shape future policies and improvements for Weather Responsive Variable Speed Limit (WRVSL) systems.
            
            **Estimated time to complete:** 10-15 minutes  
            Click **Next** to begin!
        """)
    
    elif section_num == 1:
        st.markdown("## Participant Context")
        st.session_state.responses['region'] = st.radio("Geographical region of operation:",
            options=['North America', 'Europe', 'Australia/NZ', 'Asia', 'Middle East', 'Africa', 'South America'])
        st.session_state.responses['experience'] = st.radio("Years of experience:",
            options=['<1 year', '1–3 years', '4–7 years', '8+ years'])
        st.session_state.responses['org_type'] = st.selectbox("Organization type:",
            options=['Government agency', 'Private consultancy', 'Academic', 'NGO', 'Other'])
    
    elif section_num == 2:
        st.markdown("## System Design")
        st.session_state.responses['vsl_types'] = st.multiselect("Types of VSL systems managed:",
            options=['Congestion-responsive', 'Weather-responsive', 'Event-specific', 'Other'])
    
    elif section_num == 3:
        st.markdown("## Operational Challenges")
        st.session_state.responses['driver_compliance'] = st.slider("Driver compliance issues (1-5):", 1, 5)
    
    elif section_num == 4:
        st.markdown("## Impact Assessment")
        st.session_state.responses['safety_improvement'] = st.slider("Crash reduction (%)", 0, 100)
    
    elif section_num == 5:
        st.markdown("## Lessons Learned")
        st.session_state.responses['success_story'] = st.text_area("Success story:")
    
    elif section_num == 6:
        st.markdown("## Policy & Governance")
        st.session_state.responses['regulations'] = st.multiselect("Regulatory frameworks used:",
            options=['Austroads Guidelines', 'MUTCD Section 4L', 'EU Directive 2021/034', 'Other'])
    
    elif section_num == 7:
        st.markdown("## Future Directions")
        st.session_state.responses['ai_ml'] = st.slider("AI/ML prediction models importance (1-4):", 1, 4)
    
    elif section_num == 8:
        st.markdown("## Optional Demographics")
        st.session_state.responses['follow_up'] = st.radio("Contact for follow-up?", options=['Yes', 'No'])
        if st.session_state.responses['follow_up'] == 'Yes':
            st.session_state.responses['email'] = st.text_input("Enter email:")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Call Function to Render Section ----
show_section(st.session_state.current_section)

# ---- Function to Save Responses to GitHub ----
def save_to_github(new_df):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        try:
            file = repo.get_contents(CSV_PATH)
            csv_data = file.decoded_content.decode('utf-8')
            existing_df = pd.read_csv(StringIO(csv_data))
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            file_content = updated_df.to_csv(index=False)
            repo.update_file(CSV_PATH, "Update WRVSL responses", file_content, file.sha)
        except:
            file_content = new_df.to_csv(index=False)
            repo.create_file(CSV_PATH, "Create WRVSL responses", file_content)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# ---- Navigation Buttons ----
col1, col2 = st.columns(2)
with col1:
    if st.session_state.current_section > 0:
        st.button("Previous", on_click=lambda: setattr(st.session_state, 'current_section', st.session_state.current_section - 1))
with col2:
    if st.session_state.current_section < len(SECTIONS) - 1:
        st.button("Next", on_click=lambda: setattr(st.session_state, 'current_section', st.session_state.current_section + 1))
    else:
        if st.button("Submit"):
            df = pd.DataFrame([st.session_state.responses])
            save_to_github(df)
            st.success("Responses saved successfully!")
            st.session_state.submitted = True
