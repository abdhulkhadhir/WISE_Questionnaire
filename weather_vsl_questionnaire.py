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
if 'landing' not in st.session_state:
    st.session_state.landing = True
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# ---- Landing Page ----
if st.session_state.landing:
    st.title("🌍 Global WRVSL Survey")
    st.markdown("""
        Welcome to the **Global WRVSL Survey**. Our goal is to assess the effectiveness and challenges of Weather Responsive Variable Speed Limit (WRVSL) systems. 
        Your participation is essential in shaping future implementations, policies, and technological advancements in this field.
    """)
    if st.button("Start Survey"):
        st.session_state.landing = False
    else:
        st.stop()  # Prevents further execution until "Start Survey" is clicked

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

# ---- Define simplified rating options ----
criticality_options = [
    "Most Critical",
    "Highly Critical",
    "Moderately Critical",
    "Slightly Critical",
    "Not Critical"
]

emerging_options = [
    "Most Important",
    "Highly Important",
    "Moderately Important",
    "Least Important"
]

# ---- Function to Render Sections ----
def show_section(section_num):
    st.markdown("<div class='main'>", unsafe_allow_html=True)
    
    # Section 0: Introduction & Participant Context
    if section_num == 0:
        st.subheader("Participant Context")
        st.session_state.responses['q1_region'] = st.radio(
            "1. Geographical region of operation",
            options=['North America', 'Europe', 'Australia/NZ', 'Asia', 'Middle East', 'Africa', 'South America'],
            help="Select the region where your operations are based."
        )
        st.session_state.responses['q2_experience'] = st.radio(
            "2. Years of experience with WRVSL systems",
            options=['<1 year', '1–3 years', '4–7 years', '8+ years'],
            help="Choose the option that best describes your experience."
        )
        st.session_state.responses['q3_org_type'] = st.selectbox(
            "3. Organization type",
            options=['Government agency', 'Private consultancy', 'Academic', 'NGO', 'Other'],
            help="Select the type of organization you are affiliated with."
        )
    
    # Section 1: System Design
    elif section_num == 1:
        st.subheader("System Design")
        st.session_state.responses['q4_vsl_types'] = st.multiselect(
            "4. Types of VSL systems managed",
            options=['Congestion-responsive', 'Weather-responsive', 'Event-specific', 'Other'],
            help="Select all the Variable Speed Limit systems your organization manages."
        )
        if 'Other' in st.session_state.responses.get('q4_vsl_types', []):
            st.session_state.responses['q4_vsl_other'] = st.text_input(
                "4.a. Please specify other VSL type",
                help="Enter details if your system type does not fit the listed options."
            )
        st.session_state.responses['q5_weather_params'] = st.multiselect(
            "5. Weather parameter(s) triggering speed adjustments",
            options=['Rainfall intensity', 'Snow accumulation', 'Pavement friction', 'Visibility', 'Wind speed', 'Other'],
            help="Select weather parameters that are critical in triggering speed adjustments."
        )
        st.session_state.responses['q6_verification'] = st.radio(
            "6. Verification method for weather inputs",
            options=['Cameras', 'Alternative data sources', 'None'],
            help="Choose how you verify the weather data inputs for accuracy."
        )
        if st.session_state.responses['q6_verification'] == 'Alternative data sources':
            st.session_state.responses['q6_verification_sources'] = st.text_input(
                "6.a. Specify alternative verification sources",
                help="List the alternative sources used to verify weather inputs."
            )
        st.write("""**7. Data sources used for weather inputs (Criticality Scale below)**  
        
        **Criticality Scale:**  
        - **Most Critical** – Essential and must be addressed immediately  
        - **Highly Critical** – Very important but not the highest priority  
        - **Moderately Critical** – Important but not urgent  
        - **Slightly Critical** – Somewhat important but can be deferred  
        - **Not Critical** – Minimal impact or not relevant  
        """)
        st.session_state.responses['q7_1_rwis'] = st.radio(
            "7.1 Road Weather Information System (RWIS)/roadside sensors",
            options=criticality_options,
            help="Rate the criticality of RWIS sensors."
        )
        st.session_state.responses['q7_2_vehicle_telematics'] = st.radio(
            "7.2 Connected vehicle telematics",
            options=criticality_options,
            help="Rate the criticality of connected vehicle data."
        )
        st.session_state.responses['q7_3_sat_forecasts'] = st.radio(
            "7.3 Radar/satellite forecasts",
            options=criticality_options,
            help="Rate the criticality of radar/satellite forecasts."
        )
        st.session_state.responses['q7_4_thermal_cameras'] = st.radio(
            "7.4 Thermal/visual cameras",
            options=criticality_options,
            help="Rate the criticality of thermal/visual cameras."
        )
        st.session_state.responses['q7_5_manual_reports'] = st.radio(
            "7.5 Manual operator reports",
            options=criticality_options,
            help="Rate the criticality of manual operator reports."
        )
        st.session_state.responses['q8_control_logic'] = st.radio(
            "8. Control logic architecture",
            options=['Rule-based thresholds (fixed)', 'Dynamic thresholds (real-time adjustments)', 'Machine learning based'],
            help="Select the type of control logic used in your system."
        )
        st.session_state.responses['q9_operation_mode'] = st.radio(
            "9. Mode of operation",
            options=['Alert only', 'System-recommended with operator approval', 'Fully automated'],
            help="Select the operational mode that best describes your system."
        )
        st.session_state.responses['q10_deactivation_mode'] = st.radio(
            "10. Mode of deactivation",
            options=['Manual removal', 'Automated with operator alert', 'Automated without alert'],
            help="Choose how the system is deactivated under normal conditions."
        )
        st.session_state.responses['q11_speed_adjustment'] = st.radio(
            "11. Speed adjustment protocols",
            options=['Fixed increments', 'Dynamic models', 'Operator discretion'],
            help="Select how speed adjustments are determined."
        )
        st.session_state.responses['q12_geo_coverage'] = st.radio(
            "12. Geographic coverage",
            options=['Within 5km of sensor', 'Entire carriageway', 'Overlapping zones'],
            help="Select the geographical coverage of your WRVSL system."
        )
    
    # Section 2: Operational Challenges
    elif section_num == 2:
        st.subheader("Operational Challenges")

        st.markdown("""**13. Challenge severity (Criticality Scale below)**  
        
        **Criticality Scale:**  
        - **Most Critical** – Essential and must be addressed immediately  
        - **Highly Critical** – Very important but not the highest priority  
        - **Moderately Critical** – Important but not urgent  
        - **Slightly Critical** – Somewhat important but can be deferred  
        - **Not Critical** – Minimal impact or not relevant  
        """)
        challenges = {
            "13.1 Sensor reliability": "q13_sensor_reliability",
            "13.2 Driver compliance": "q13_driver_compliance",
            "13.3 Maintenance costs": "q13_maintenance_costs",
            "13.4 Inter-agency coordination": "q13_coordination",
            "13.5 Operational FTE/resources": "q13_fte_challenge"
        }
        for label, key in challenges.items():
            st.session_state.responses[key] = st.radio(
                label,
                options=criticality_options,
                help=f"Rate the severity of {label.split()[1].lower()}."
            )
        st.session_state.responses['q14_mitigation_strategies'] = st.multiselect(
            "14. Mitigation strategies for non-compliance",
            options=['Public education campaigns', 'Dynamic signage with penalty warnings', 'Automated enforcement', 'None'],
            help="Select all strategies you employ to address non-compliance."
        )
    
    # Section 3: Impact Assessment
    elif section_num == 3:
        st.subheader("Impact Assessment")
        st.session_state.responses['q15_primary_crash_reduction'] = st.slider(
            "15. Primary crash reduction (%)",
            0, 100, help="Estimate the percentage improvement in safety (primary crash reduction) due to WRVSL."
        )
        st.session_state.responses['q16_secondary_crash_reduction'] = st.slider(
            "16. Secondary crash reduction (%)",
            0, 100, help="Estimate the percentage improvement in safety (secondary crash reduction) due to WRVSL."
        )
        st.session_state.responses['q17_safety_source'] = st.radio(
            "17. Data source for safety improvement",
            options=['Field', 'Simulation'],
            help="Select whether the safety data is based on field observations or simulation results."
        )
        st.session_state.responses['q18_speed_compliance'] = st.slider(
            "18. Speed compliance rate (%)",
            0, 100, help="Indicate the observed or expected speed compliance rate."
        )
        st.session_state.responses['q19_speed_source'] = st.radio(
            "19. Data source for speed compliance",
            options=['Field', 'Simulation'],
            help="Select whether the speed compliance data is based on field data or simulation."
        )
    
    # Section 4: Lessons Learned
    elif section_num == 4:
        st.subheader("Lessons Learned")
        st.session_state.responses['q20_success_story'] = st.text_area(
            "20. Success story (Max 200 words)",
            help="Share a success story related to WRVSL implementation. Please keep within 200 words."
        )
        st.session_state.responses['q21_unexpected_challenges'] = st.text_area(
            "21. Unexpected challenges & resolution (Max 150 words)",
            help="Describe any unforeseen challenges and how they were addressed, keeping within 150 words."
        )
    
    # Section 5: Policy & Governance
    elif section_num == 5:
        st.subheader("Policy & Governance")
        st.session_state.responses['q22_regulations'] = st.multiselect(
            "22. Regulatory frameworks used",
            options=['Austroads Guidelines', 'MUTCD Section 4L', 'EU Directive 2021/034', 'Other'],
            help="Select all regulatory frameworks that influence your system."
        )
        if 'Other' in st.session_state.responses.get('q22_regulations', []):
            st.session_state.responses['q22_regulations_other'] = st.text_input(
                "22.a. Please specify other regulatory frameworks",
                help="Enter additional details if other regulatory frameworks apply."
            )
        st.markdown("**23. Multi-agency collaboration frequency**")
        st.session_state.responses['q23_meteorology'] = st.radio(
            "23.1 Meteorological department",
            options=['Daily', 'Weekly', 'Monthly', 'Never'],
            help="How often do you collaborate with the meteorological department?"
        )
        st.session_state.responses['q23_law_enforcement'] = st.radio(
            "23.2 Law enforcement",
            options=['Daily', 'Weekly', 'Monthly', 'Never'],
            help="How frequently is there interaction with law enforcement?"
        )
        st.session_state.responses['q23_road_maintenance'] = st.radio(
            "23.3 Road maintenance teams",
            options=['Daily', 'Weekly', 'Monthly', 'Never'],
            help="Indicate how often you engage with road maintenance teams."
        )
    
    # Section 6: Future Directions
    elif section_num == 6:
        st.subheader("Future Directions")
        st.markdown("""**24. Rank emerging technologies (Ranking Scale below)**  
        
Ranking Scale:  
• Most Important – Game-changing technology with immediate and significant impact  
• Highly Important – Strong potential for impact but not the top priority  
• Moderately Important – Has relevance but not a critical focus area  
• Least Important – Low impact or not a priority at this time""")
        st.session_state.responses['q24_ai_ml'] = st.radio(
            "24.1 AI/ML prediction models",
            options=emerging_options,
            help="Select the ranking for AI/ML models for predicting weather-related impacts."
        )
        st.session_state.responses['q24_iot_sensors'] = st.radio(
            "24.2 Satellite-connected IoT sensors",
            options=emerging_options,
            help="Select the ranking for IoT sensors in your system."
        )
        st.session_state.responses['q24_cv_integration'] = st.radio(
            "24.3 Connected vehicle integration",
            options=emerging_options,
            help="Select the ranking for connected vehicle data integration."
        )
        st.session_state.responses['q25_research_gaps'] = st.text_area(
            "25. Research gaps hindering WRVSL advancements (100 words max)",
            help="Briefly describe the research gaps that need to be addressed to advance WRVSL technology."
        )
    
    # Section 7: Optional Demographics
    elif section_num == 7:
        st.subheader("Optional Demographics")
        st.session_state.responses['q26_follow_up'] = st.radio(
            "26. Contact for follow-up?",
            options=['Yes', 'No'],
            help="Indicate if you are willing to be contacted for follow-up questions."
        )
        if st.session_state.responses['q26_follow_up'] == 'Yes':
            st.session_state.responses['q27_email'] = st.text_input(
                "27. Enter email",
                help="Please provide your email address for further contact."
            )
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
