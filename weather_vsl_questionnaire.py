import streamlit as st
import pandas as pd
import json
import base64
import logging
from github import Github
from io import StringIO

# ---- Streamlit Page Config ----
st.set_page_config(page_title="Global WRVSL Survey", layout="wide")

# ---- Custom CSS for Enhanced Visual Appeal ----
st.markdown("""
    <style>
        body {
            background-color: #f8f9fa;
        }
        .main {
            background-color: #ffffff;
            padding: 2rem;
            margin: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 1rem;
        }
        .progress-bar {
            margin-bottom: 1rem;
        }
        h1, h2, h3, h4 {
            color: #333366;
        }
    </style>
    """, unsafe_allow_html=True)

# ---- Title & Introduction ----
st.title("🌍 Global WRVSL Survey")
st.markdown("""
    Welcome to the **Global WRVSL Survey**. Our goal is to assess the effectiveness and challenges of Weather Responsive Variable Speed Limit (WRVSL) systems. 
    Your participation is essential in shaping future implementations, policies, and technological advancements in this field.
""")
st.markdown("---")

# ---- GitHub Configuration ----
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "abdhulkhadhir/WISE_Questionnaire"
CSV_PATH = "responses.csv"

# ---- Define Survey Sections ----
SECTIONS = [
    "Introduction & Participant Context",
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
        if st.sidebar.button(section, key=f"btn_{i}"):
            st.session_state.current_section = i

# ---- Function to Render Sections ----
def show_section(section_num):
    st.markdown("<div class='main'>", unsafe_allow_html=True)
    
    # Section 0: Introduction & Participant Context
    if section_num == 0:
        st.title("Global WRVSL Survey")
        st.markdown("""
            Welcome to the Global WRVSL Survey. Our goal is to assess the effectiveness of WRVSL systems.
            Please provide your details and context below.
        """)
        st.markdown("---")
        st.subheader("Participant Context")
        st.session_state.responses['region'] = st.radio(
            "1. Geographical region of operation",
            options=['North America', 'Europe', 'Australia/NZ', 'Asia', 'Middle East', 'Africa', 'South America'],
            help="Select the region where your operations are based."
        )
        st.session_state.responses['experience'] = st.radio(
            "2. Years of experience with WRVSL systems",
            options=['<1 year', '1–3 years', '4–7 years', '8+ years'],
            help="Choose the option that best describes your experience."
        )
        st.session_state.responses['org_type'] = st.selectbox(
            "3. Organization type",
            options=['Government agency', 'Private consultancy', 'Academic', 'NGO', 'Other'],
            help="Select the type of organization you are affiliated with."
        )
    
    # Section 1: System Design
    elif section_num == 1:
        st.subheader("System Design")
        st.session_state.responses['vsl_types'] = st.multiselect(
            "4. Types of VSL systems managed",
            options=['Congestion-responsive', 'Weather-responsive', 'Event-specific', 'Other'],
            help="Select all the Variable Speed Limit systems your organization manages."
        )
        if 'Other' in st.session_state.responses['vsl_types']:
            st.session_state.responses['vsl_other'] = st.text_input(
                "Please specify other VSL type",
                help="Enter details if your system type does not fit the listed options."
            )
        st.session_state.responses['weather_params'] = st.multiselect(
            "5. Weather parameter(s) triggering speed adjustments",
            options=['Rainfall intensity', 'Snow accumulation', 'Pavement friction', 'Visibility', 'Wind speed', 'Other'],
            help="Select weather parameters that are critical in triggering speed adjustments."
        )
        verification = st.radio(
            "6. Verification method for weather inputs",
            options=['Cameras', 'Alternative data sources', 'None'],
            help="Choose how you verify the weather data inputs for accuracy."
        )
        st.session_state.responses['verification_method'] = verification
        if verification == 'Alternative data sources':
            st.session_state.responses['verification_sources'] = st.text_input(
                "Specify alternative verification sources",
                help="List the alternative sources used to verify weather inputs."
            )
        st.markdown("**7. Data sources used for weather inputs (Rank 1–5, 1=Most Critical)**")
        st.session_state.responses['rw_sensors'] = st.slider(
            "RWIS/roadside sensors", 1, 5, help="Rank the criticality of RWIS sensors."
        )
        st.session_state.responses['vehicle_telematics'] = st.slider(
            "Connected vehicle telematics", 1, 5, help="Rank the importance of connected vehicle data."
        )
        st.session_state.responses['sat_forecasts'] = st.slider(
            "Radar/satellite forecasts", 1, 5, help="Rank the importance of radar/satellite forecasts."
        )
        st.session_state.responses['thermal_cameras'] = st.slider(
            "Thermal/visual cameras", 1, 5, help="Rank the criticality of thermal/visual cameras."
        )
        st.session_state.responses['manual_reports'] = st.slider(
            "Manual operator reports", 1, 5, help="Rate the importance of manual operator reports."
        )
        st.session_state.responses['control_logic'] = st.radio(
            "8. Control logic architecture",
            options=['Rule-based thresholds (fixed)', 'Dynamic thresholds (real-time adjustments)', 'Machine learning based'],
            help="Select the type of control logic used in your system."
        )
        st.session_state.responses['operation_mode'] = st.radio(
            "9. Mode of operation",
            options=['Alert only', 'System-recommended with operator approval', 'Fully automated'],
            help="Select the operational mode that best describes your system."
        )
        st.session_state.responses['deactivation_mode'] = st.radio(
            "10. Mode of deactivation",
            options=['Manual removal', 'Automated with operator alert', 'Automated without alert'],
            help="Choose how the system is deactivated under normal conditions."
        )
        st.session_state.responses['speed_adjustment'] = st.radio(
            "11. Speed adjustment protocols",
            options=['Fixed increments', 'Dynamic models', 'Operator discretion'],
            help="Select how speed adjustments are determined."
        )
        st.session_state.responses['geo_coverage'] = st.radio(
            "12. Geographic coverage",
            options=['Within 5km of sensor', 'Entire carriageway', 'Overlapping zones'],
            help="Select the geographical coverage of your WRVSL system."
        )
    
    # Section 2: Operational Challenges
    elif section_num == 2:
        st.subheader("Operational Challenges")
        st.markdown("**13. Challenge severity (Rate 1–5, 1=Minor, 5=Critical)**")
        challenges = {
            'Sensor reliability': 'sensor_reliability',
            'Driver compliance': 'driver_compliance',
            'Maintenance costs': 'maintenance_costs',
            'Inter-agency coordination': 'coordination',
            'Operational FTE/resources': 'fte_challenge'
        }
        for label, key in challenges.items():
            st.session_state.responses[key] = st.slider(
                label, 1, 5, help=f"Rate the severity of {label.lower()}."
            )
        st.session_state.responses['mitigation_strategies'] = st.multiselect(
            "14. Mitigation strategies for non-compliance",
            options=['Public education campaigns', 'Dynamic signage with penalty warnings', 'Automated enforcement', 'None'],
            help="Select all strategies you employ to address non-compliance."
        )
    
    # Section 3: Impact Assessment
    elif section_num == 3:
        st.subheader("Impact Assessment")
        st.session_state.responses['safety_improvement'] = st.slider(
            "15. Crash reduction (%)", 0, 100,
            help="Estimate the percentage improvement in safety (crash reduction) due to WRVSL."
        )
        st.session_state.responses['safety_source'] = st.radio(
            "Data source for safety improvement",
            options=['Field', 'Simulation'],
            help="Select whether the safety data is based on field observations or simulation results."
        )
        st.session_state.responses['speed_compliance'] = st.slider(
            "16. Speed compliance rate (%)", 0, 100,
            help="Indicate the observed or expected speed compliance rate."
        )
        st.session_state.responses['speed_source'] = st.radio(
            "Data source for speed compliance",
            options=['Field', 'Simulation'],
            help="Select whether the speed compliance data is based on field data or simulation."
        )
    
    # Section 4: Lessons Learned
    elif section_num == 4:
        st.subheader("Lessons Learned")
        st.session_state.responses['success_story'] = st.text_area(
            "17. Success story (Max 200 words)",
            help="Share a success story related to WRVSL implementation. Please keep within 200 words."
        )
        st.session_state.responses['unexpected_challenges'] = st.text_area(
            "18. Unexpected challenges & resolution (Max 150 words)",
            help="Describe any unforeseen challenges and how they were addressed, keeping within 150 words."
        )
    
    # Section 5: Policy & Governance
    elif section_num == 5:
        st.subheader("Policy & Governance")
        st.session_state.responses['regulations'] = st.multiselect(
            "19. Regulatory frameworks used",
            options=['Austroads Guidelines', 'MUTCD Section 4L', 'EU Directive 2021/034', 'Other'],
            help="Select all regulatory frameworks that influence your system."
        )
        st.markdown("**20. Multi-agency collaboration frequency**")
        st.session_state.responses['meteorology'] = st.radio(
            "Meteorological department",
            options=['Daily', 'Weekly', 'Monthly', 'Never'],
            help="How often do you collaborate with the meteorological department?"
        )
        st.session_state.responses['law_enforcement'] = st.radio(
            "Law enforcement",
            options=['Daily', 'Weekly', 'Monthly', 'Never'],
            help="How frequently is there interaction with law enforcement?"
        )
        st.session_state.responses['road_maintenance'] = st.radio(
            "Road maintenance teams",
            options=['Daily', 'Weekly', 'Monthly', 'Never'],
            help="Indicate how often you engage with road maintenance teams."
        )
    
    # Section 6: Future Directions
    elif section_num == 6:
        st.subheader("Future Directions")
        st.markdown("**21. Rank emerging technologies (1=Most Important, 4=Least Important)**")
        st.session_state.responses['ai_ml'] = st.slider(
            "AI/ML prediction models", 1, 4, help="Rank AI/ML models for predicting weather-related impacts."
        )
        st.session_state.responses['iot_sensors'] = st.slider(
            "Satellite-connected IoT sensors", 1, 4, help="Rank the importance of IoT sensors in your system."
        )
        st.session_state.responses['cv_integration'] = st.slider(
            "Connected vehicle integration", 1, 4, help="Rate the importance of connected vehicle data integration."
        )
        st.session_state.responses['research_gaps'] = st.text_area(
            "22. Research gaps hindering WRVSL advancements (100 words max)",
            help="Briefly describe the research gaps that need to be addressed to advance WRVSL technology."
        )
    
    # Section 7: Optional Demographics
    elif section_num == 7:
        st.subheader("Optional Demographics")
        st.session_state.responses['follow_up'] = st.radio(
            "23. Contact for follow-up?",
            options=['Yes', 'No'],
            help="Indicate if you are willing to be contacted for follow-up questions."
        )
        if st.session_state.responses['follow_up'] == 'Yes':
            st.session_state.responses['email'] = st.text_input(
                "Enter email",
                help="Please provide your email address for further contact."
            )
        # Review Section - expand to show current responses before submission
        with st.expander("Review Your Answers"):
            st.write(st.session_state.responses)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Call Function to Render Section ----
show_section(st.session_state.current_section)

# ---- Function to Save and Append Responses to GitHub ----
def save_to_github(new_df):
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        try:
            # Attempt to get the existing file from the repository
            file = repo.get_contents(CSV_PATH)
            csv_data = file.decoded_content.decode('utf-8')
            existing_df = pd.read_csv(StringIO(csv_data))
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            file_content = updated_df.to_csv(index=False)
            repo.update_file(CSV_PATH, "Update WRVSL responses", file_content, file.sha)
        except Exception as e:
            # If the file doesn't exist, create a new one with the new response
            file_content = new_df.to_csv(index=False)
            repo.create_file(CSV_PATH, "Create WRVSL responses", file_content)
    except Exception as e:
        logging.error(f"Error saving to GitHub: {e}")

# ---- Navigation Button Callbacks ----
def previous_section():
    st.session_state.current_section -= 1

def next_section():
    st.session_state.current_section += 1

# ---- Navigation Buttons ----
col1, col2 = st.columns(2)
with col1:
    if st.session_state.current_section > 0:
        st.button("⬅️ Previous", on_click=previous_section)
with col2:
    if st.session_state.current_section < len(SECTIONS) - 1:
        st.button("Next ➡️", on_click=next_section)
    else:
        if st.button("✅ Submit"):
            df = pd.DataFrame([st.session_state.responses])
            save_to_github(df)
            st.success("Responses saved successfully! 🎉")
            st.session_state.submitted = True
