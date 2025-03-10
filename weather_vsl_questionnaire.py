import streamlit as st
import pandas as pd
import json
import base64
from github import Github

# ---- Streamlit Page Config ----
st.set_page_config(page_title="Global VSL Survey", layout="wide")

# ---- GitHub Configuration ----
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "abdhulkhadhir/qd_visualiser"
CSV_PATH = "responses.csv"

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
st.sidebar.progress(progress)

for i, section in enumerate(SECTIONS):
    if i == st.session_state.current_section:
        st.sidebar.markdown(f"➡️ **{section}**")
    else:
        if st.sidebar.button(section):
            st.session_state.current_section = i
            st.rerun()

# ---- Function to Render Sections ----
def show_section(section_num):
    """Renders the current survey section."""
    st.markdown(f"## {SECTIONS[section_num]}")

    if section_num == 0:  # Participant Context
        st.session_state.responses['region'] = st.radio("**1. Geographical region of operation**", ['North America', 'Europe', 'Australia/NZ', 'Asia', 'Middle East', 'Africa', 'South America'])
        st.session_state.responses['experience'] = st.radio("**2. Years of experience with WRVSL systems**", ['<1 year', '1–3 years', '4–7 years', '8+ years'])
        st.session_state.responses['org_type'] = st.selectbox("**3. Organization type**", ['Government agency', 'Private consultancy', 'Academic', 'NGO', 'Other'])

    elif section_num == 1:  # System Design
        st.session_state.responses['vsl_types'] = st.multiselect("**4. Types of VSL systems managed**", ['Congestion-responsive', 'Weather-responsive', 'Event-specific', 'Other'])
        st.session_state.responses['weather_params'] = st.multiselect("**5. Primary weather parameters triggering adjustments**", ['Rainfall intensity', 'Snow accumulation', 'Pavement friction', 'Visibility', 'Wind speed', 'Humidity', 'Other'])
        st.session_state.responses['data_sources'] = st.text_area("**6. Rank data sources used for weather inputs (1=Most Critical, 5=Least)**", "RWIS/roadside sensors, Connected vehicle telematics, Radar/satellite forecasts, Thermal cameras, Manual operator reports")
        st.session_state.responses['control_logic'] = st.radio("**7. Control logic architecture**", ['Rule-based thresholds (fixed)', 'Dynamic thresholds (real-time adjustments)', 'Machine learning based'])
        if st.session_state.responses['control_logic'] == 'Rule-based thresholds (fixed)':
            st.session_state.responses['rule_based_thresholds'] = st.radio("**Threshold determination method**", ['Historical crash data', 'Regulatory guidelines', 'Trial-and-error', 'Other'])
        st.session_state.responses['speed_adjustment'] = st.radio("**8. Speed adjustment protocols**", ['Fixed increments', 'Dynamic models', 'Operator discretion'])

    elif section_num == 2:  # Operational Challenges
        st.markdown("**9. Challenge severity (Rate 1–5, 1=Minor, 5=Critical)**")
        st.session_state.responses['sensor_reliability'] = st.slider("Sensor reliability", 1, 5)
        st.session_state.responses['driver_compliance'] = st.slider("Driver compliance", 1, 5)
        st.session_state.responses['maintenance_costs'] = st.slider("Maintenance costs", 1, 5)
        st.session_state.responses['coordination'] = st.slider("Inter-agency coordination", 1, 5)
        st.session_state.responses['mitigation_strategies'] = st.multiselect("**10. Mitigation strategies for non-compliance**", ['Public education campaigns', 'Dynamic signage with penalty warnings', 'Automated enforcement', 'None'])

    elif section_num == 3:  # Impact Assessment
        st.session_state.responses['safety_improvement'] = st.slider("**11. Crash reduction (%)**", 0, 100)
        st.session_state.responses['safety_source'] = st.radio("**Data source**", ['Field', 'Simulation'])
        st.session_state.responses['speed_compliance'] = st.slider("**12. Speed compliance rate (%)**", 0, 100)

    elif section_num == 4:  # Lessons Learned
        st.session_state.responses['success_story'] = st.text_area("**13. Success story (Max 200 words)**")
        st.session_state.responses['unexpected_challenges'] = st.text_area("**14. Unexpected challenges & resolution (Max 150 words)**")

    elif section_num == 5:  # Policy & Governance
        st.session_state.responses['regulations'] = st.multiselect("**16. Regulatory frameworks used**", ['Austroads Guidelines', 'MUTCD Section 4L', 'EU Directive 2021/034', 'Other'])
        st.markdown("**17. Multi-agency collaboration frequency**")
        st.session_state.responses['meteorology'] = st.radio("Meteorological department", ['Daily', 'Weekly', 'Monthly', 'Never'])
        st.session_state.responses['law_enforcement'] = st.radio("Law enforcement", ['Daily', 'Weekly', 'Monthly', 'Never'])
        st.session_state.responses['road_maintenance'] = st.radio("Road maintenance teams", ['Daily', 'Weekly', 'Monthly', 'Never'])

    elif section_num == 6:  # Future Directions
        st.session_state.responses['emerging_tech'] = st.text_area("**18. Rank emerging technologies (1=Most important, 4=Least)**", "AI/ML prediction models, Satellite-connected IoT sensors, Connected vehicle integration")
        st.session_state.responses['research_gaps'] = st.text_area("**19. Research gaps hindering WRVSL advancements (100 words max)**")

    elif section_num == 7:  # Optional Demographics
        st.session_state.responses['follow_up'] = st.radio("**20. Contact for follow-up?**", ['Yes', 'No'])
        if st.session_state.responses['follow_up'] == 'Yes':
            st.session_state.responses['email'] = st.text_input("Enter email")

# ---- Save Responses to GitHub ----
def save_to_github(df):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    repo.create_file(CSV_PATH, "Create VSL responses file", df.to_csv(index=False))

# ---- Navigation ----
show_section(st.session_state.current_section)

if st.button("Next Section →"):
    st.session_state.current_section += 1
    st.rerun()

if st.session_state.current_section == len(SECTIONS) - 1 and st.button("Submit"):
    df = pd.DataFrame([st.session_state.responses])
    save_to_github(df)
    st.success("Responses saved successfully!")
