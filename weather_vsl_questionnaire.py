import streamlit as st
import pandas as pd
import json
import base64
import logging
from github import Github

# ---- Streamlit Page Config ----
st.set_page_config(page_title="Global WRVSL Survey", layout="wide")
st.markdown("""
### Definitions
**WRVSL (Weather-Responsive Variable Speed Limit):** Systems dynamically adjusting speed limits based on real-time weather conditions.  
**VSL (Variable Speed Limit):** Broader category including weather-responsive, congestion-responsive, and event-specific systems.
""")

# ---- GitHub Configuration ----
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "abdhulkhadhir/WISE_Questionnaire"
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
        st.session_state.responses['region'] = st.radio("**1. Geographical region of operation**", 
            ['North America', 'Europe', 'Australia/NZ', 'Asia', 'Middle East', 'Africa', 'South America'])
        st.session_state.responses['experience'] = st.radio("**2. Years of experience with WRVSL systems**", 
            ['<1 year', '1–3 years', '4–7 years', '8+ years'])
        st.session_state.responses['org_type'] = st.selectbox("**3. Organization type**", 
            ['Government agency', 'Private consultancy', 'Academic', 'NGO', 'Other'])

    elif section_num == 1:  # System Design
        vsl_selection = st.multiselect("**4. Types of VSL systems managed**", 
            ['Congestion-responsive', 'Weather-responsive', 'Event-specific', 'Other'])
        st.session_state.responses['vsl_types'] = vsl_selection
        if 'Other' in vsl_selection:
            st.session_state.responses['vsl_other'] = st.text_input("Specify other VSL type")

        st.session_state.responses['weather_params'] = st.multiselect("**5. Weather parameter(s) triggering speed adjustments**", 
            ['Rainfall intensity', 'Snow accumulation', 'Pavement friction', 'Visibility', 'Wind speed', 'Other'])

        # New verification question
        verification = st.radio("**6. Verification method for weather inputs**",
            ['Cameras', 'Alternative data sources', 'None'])
        if verification == 'Alternative data sources':
            st.session_state.responses['verification_sources'] = st.text_input("Specify alternative verification sources")

        st.markdown("**7. Data sources used for weather inputs (Rank 1–5, 1=Most Critical)**")
        st.session_state.responses['rw_sensors'] = st.slider("RWIS/roadside sensors", 1, 5)
        st.session_state.responses['vehicle_telematics'] = st.slider("Connected vehicle telematics", 1, 5)
        st.session_state.responses['sat_forecasts'] = st.slider("Radar/satellite forecasts", 1, 5)
        st.session_state.responses['thermal_cameras'] = st.slider("Thermal/visual cameras", 1, 5)
        st.session_state.responses['manual_reports'] = st.slider("Manual operator reports", 1, 5)

        st.session_state.responses['control_logic'] = st.radio("**8. Control logic architecture**", 
            ['Rule-based thresholds (fixed)', 'Dynamic thresholds (real-time adjustments)', 'Machine learning based'])
        
        # New mode questions
        st.session_state.responses['operation_mode'] = st.radio("**9. Mode of operation**",
            ['Alert only', 'System-recommended with operator approval', 'Fully automated'])
        
        st.session_state.responses['deactivation_mode'] = st.radio("**10. Mode of deactivation**",
            ['Manual removal', 'Automated with operator alert', 'Automated without alert'])

        st.session_state.responses['speed_adjustment'] = st.radio("**11. Speed adjustment protocols**", 
            ['Fixed increments', 'Dynamic models', 'Operator discretion'])

        # New geographic coverage
        st.session_state.responses['geo_coverage'] = st.radio("**12. Geographic coverage**",
            ['Within 5km of sensor', 'Entire carriageway', 'Overlapping zones'])

    elif section_num == 2:  # Operational Challenges
        st.markdown("**13. Challenge severity (Rate 1–5, 1=Minor, 5=Critical)**")
        challenges = {
            'Sensor reliability': 'sensor_reliability',
            'Driver compliance': 'driver_compliance',
            'Maintenance costs': 'maintenance_costs',
            'Inter-agency coordination': 'coordination',
            'Operational FTE/resources': 'fte_challenge'  # New challenge
        }
        
        for label, key in challenges.items():
            st.session_state.responses[key] = st.slider(label, 1, 5)
        
        st.session_state.responses['mitigation_strategies'] = st.multiselect("**14. Mitigation strategies for non-compliance**", 
            ['Public education campaigns', 'Dynamic signage with penalty warnings', 'Automated enforcement', 'None'])

    elif section_num == 3:  # Impact Assessment
        st.session_state.responses['safety_improvement'] = st.slider("**15. Crash reduction (%)**", 0, 100)
        st.session_state.responses['safety_source'] = st.radio("**Data source**", ['Field', 'Simulation'])
        st.session_state.responses['speed_compliance'] = st.slider("**16. Speed compliance rate (%)**", 0, 100)
        st.session_state.responses['speed_source'] = st.radio("**Data source**", ['Field', 'Simulation'])

    elif section_num == 4:  # Lessons Learned
        st.session_state.responses['success_story'] = st.text_area("**17. Success story (Max 200 words)**")
        st.session_state.responses['unexpected_challenges'] = st.text_area("**18. Unexpected challenges & resolution (Max 150 words)**")

    elif section_num == 5:  # Policy & Governance
        st.session_state.responses['regulations'] = st.multiselect("**19. Regulatory frameworks used**", 
            ['Austroads Guidelines', 'MUTCD Section 4L', 'EU Directive 2021/034', 'Other'])
        st.markdown("**20. Multi-agency collaboration frequency**")
        st.session_state.responses['meteorology'] = st.radio("Meteorological department", 
            ['Daily', 'Weekly', 'Monthly', 'Never'])
        st.session_state.responses['law_enforcement'] = st.radio("Law enforcement", 
            ['Daily', 'Weekly', 'Monthly', 'Never'])
        st.session_state.responses['road_maintenance'] = st.radio("Road maintenance teams", 
            ['Daily', 'Weekly', 'Monthly', 'Never'])

    elif section_num == 6:  # Future Directions
        st.markdown("**21. Rank emerging technologies (1=Most Important, 4=Least Important)**")
        st.session_state.responses['ai_ml'] = st.slider("AI/ML prediction models", 1, 4)
        st.session_state.responses['iot_sensors'] = st.slider("Satellite-connected IoT sensors", 1, 4)
        st.session_state.responses['cv_integration'] = st.slider("Connected vehicle integration", 1, 4)
        st.session_state.responses['research_gaps'] = st.text_area("**22. Research gaps hindering WRVSL advancements (100 words max)**")

    elif section_num == 7:  # Optional Demographics
        st.session_state.responses['follow_up'] = st.radio("**23. Contact for follow-up?**", ['Yes', 'No'])
        if st.session_state.responses['follow_up'] == 'Yes':
            st.session_state.responses['email'] = st.text_input("Enter email")

# ---- Call Function to Render Section ----
show_section(st.session_state.current_section)

# ---- Save Responses to GitHub ----
def save_to_github(df):
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file_content = df.to_csv(index=False)

        try:
            file = repo.get_contents(CSV_PATH)
            repo.update_file(CSV_PATH, "Update WRVSL responses", file_content, file.sha)
        except Exception as e:
            repo.create_file(CSV_PATH, "Create WRVSL responses", file_content)

    except Exception as e:
        logging.error(f"Error saving to GitHub: {e}")

# ---- Navigation Buttons ----
col1, col2 = st.columns([1, 1])
with col1:
    if st.session_state.current_section > 0:
        st.button("Previous", on_click=lambda: st.session_state.update(current_section=st.session_state.current_section-1))

with col2:
    if st.session_state.current_section < len(SECTIONS) - 1:
        st.button("Next", on_click=lambda: st.session_state.update(current_section=st.session_state.current_section+1))
    else:
        if st.button("Submit"):
            df = pd.DataFrame([st.session_state.responses])
            save_to_github(df)
            st.success("Responses saved successfully!")
            st.session_state.submitted = True
