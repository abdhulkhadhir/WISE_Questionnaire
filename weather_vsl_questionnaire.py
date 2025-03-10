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
        vsl_selection = st.multiselect("**4. Types of VSL systems managed**", ['Congestion-responsive', 'Weather-responsive', 'Event-specific', 'Other'])
        st.session_state.responses['vsl_types'] = vsl_selection
        if 'Other' in vsl_selection:
            st.session_state.responses['vsl_other'] = st.text_input("Specify other VSL type")

        st.session_state.responses['weather_params'] = st.multiselect("**5. Primary weather parameters triggering adjustments**", ['Rainfall intensity', 'Snow accumulation', 'Pavement friction', 'Visibility', 'Wind speed', 'Humidity', 'Other'])

        st.markdown("**6. Rate the importance of data sources (1=Least Important, 5=Most Important)**")
        st.session_state.responses['rw_sensors'] = st.slider("RWIS/roadside sensors", 1, 5)
        st.session_state.responses['vehicle_telematics'] = st.slider("Connected vehicle telematics", 1, 5)
        st.session_state.responses['sat_forecasts'] = st.slider("Radar/satellite forecasts", 1, 5)
        st.session_state.responses['thermal_cameras'] = st.slider("Thermal cameras", 1, 5)
        st.session_state.responses['manual_reports'] = st.slider("Manual operator reports", 1, 5)

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
        st.session_state.responses['safety_improvement'] = st.slider("**11. Crash reduction (%)**", 0, 100, key="safety_improvement_slider")
        st.session_state.responses['safety_source'] = st.radio("**Data source**", ['Field', 'Simulation'], key="safety_source_radio")
        st.session_state.responses['speed_compliance'] = st.slider("**12. Speed compliance rate (%)**", 0, 100, key="speed_compliance_slider")
        st.session_state.responses['speed_source'] = st.radio("**Data source**", ['Field', 'Simulation'], key="speed_source_radio")

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
        st.markdown("**18. Rank emerging technologies (1=Most Important, 4=Least Important)**")
        st.session_state.responses['ai_ml'] = st.slider("AI/ML prediction models", 1, 4)
        st.session_state.responses['iot_sensors'] = st.slider("Satellite-connected IoT sensors", 1, 4)
        st.session_state.responses['cv_integration'] = st.slider("Connected vehicle integration", 1, 4)
        st.session_state.responses['research_gaps'] = st.text_area("**19. Research gaps hindering WRVSL advancements (100 words max)**")

    elif section_num == 7:  # Optional Demographics
        st.session_state.responses['follow_up'] = st.radio("**20. Contact for follow-up?**", ['Yes', 'No'])
        if st.session_state.responses['follow_up'] == 'Yes':
            st.session_state.responses['email'] = st.text_input("Enter email")

# ---- Call Function to Render Section ----
show_section(st.session_state.current_section)

# ---- Navigation Buttons ----
if st.session_state.current_section > 0:
    if st.button("Previous"):
        st.session_state.current_section -= 1
        st.rerun()

if st.session_state.current_section < len(SECTIONS) - 1:
    if st.button("Next"):
        st.session_state.current_section += 1
        st.rerun()
else:
    if st.button("Submit"):
        st.success("Responses saved successfully!")
