import streamlit as st
import pandas as pd
import os

CSV_FILE = 'responses.csv'

def save_response(data):
    file_exists = os.path.isfile(CSV_FILE)
    df = pd.DataFrame([data])
    if file_exists:
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, mode='w', header=True, index=False)

st.set_page_config(page_title="Weather-Responsive VSL Survey", layout="wide")
st.title("🌍 Weather-Responsive Variable Speed Limits (VSL) Survey")
st.write("**Purpose:** Identify global best practices and challenges in weather-responsive VSL implementations.")
st.write("**Ethics Approval:** <QUT Ethics approval #> | All responses anonymized")
st.write("**Estimated Time:** 12–15 minutes")

with st.form("survey_form"):
    st.header("📝 Section 1: Consent and Introduction")
    consent = st.checkbox("I consent to participate in this anonymous study")
    data_use = st.checkbox("I agree to terms of data use for academic research <add terms>")
    
    st.header("🌍 Section 2: Practitioner Background (15% Complete)")
    geographical_context = st.selectbox("In which country/region do you primarily work?", ["North America", "Europe", "Australia/NZ", "Asia", "Middle East", "Africa", "South America"], help="Select your primary region of professional work.")
    role = st.selectbox("Select your primary role", ["Traffic Operations Manager", "Transportation Engineer", "Policy Advisor", "Researcher/Academic", "Other"], help="Choose the role that best describes your profession.")
    role_other = st.text_input("Please specify your role") if role == "Other" else ""
    experience = st.selectbox("How many years have you worked with weather-responsive VSL implementations?", ["<1 year", "1–3 years", "4–7 years", "8+ years"], help="Select the range that best fits your experience.")

    st.header("⚙️ Section 3: VSL System Design (35% Complete)")
    weather_params = st.multiselect("Select the 3 most critical weather parameters influencing VSL", ["Visibility", "Precipitation intensity", "Pavement temperature", "Wind speed", "Road friction", "Humidity", "Other"], help="Choose up to three parameters that most impact VSL decisions.")
    weather_params_other = st.text_input("Specify other weather parameters") if "Other" in weather_params else ""
    
    st.write("### Rank data sources used for VSL decisions (1 = Most Important, 5 = Least Important)")
    data_sources = {
        "Roadside Weather Information System (RWIS)": st.number_input("RWIS", 1, 5, help="Fixed stations collecting real-time weather data."),
        "Connected Vehicle Telematics": st.number_input("Connected Vehicle Telematics", 1, 5, help="Data from vehicles equipped with sensors."),
        "CCTV/Thermal Cameras": st.number_input("CCTV/Thermal Cameras", 1, 5, help="Video-based monitoring systems."),
        "Weather Radar Forecasts": st.number_input("Weather Radar Forecasts", 1, 5, help="Predictive weather modeling."),
        "Manual Operator Input": st.number_input("Manual Operator Input", 1, 5, help="Decisions made by traffic control operators.")
    }
    
    control_logic = st.selectbox("Which control logic does your system primarily use?", ["Rule-Based Thresholds", "Fuzzy Logic", "Machine Learning", "Model Predictive Control", "Hybrid Approach"], help="Select the method used to determine VSL adjustments.")

    st.header("⚠️ Section 4: Operational Challenges (60% Complete)")
    st.write("### Rate the significance of the following challenges in your VSL operations (1 = Not Significant, 5 = Critical)")
    driver_compliance = st.slider("Driver Compliance", 1, 5, help="How well do drivers adhere to VSL changes?")
    sensor_reliability = st.slider("Sensor Reliability", 1, 5, help="Issues with accuracy and functionality of sensors.")
    cybersecurity_risks = st.slider("Cybersecurity Risks", 1, 5, help="Concerns about hacking or data breaches.")
    multi_agency_coordination = st.slider("Multi-Agency Coordination", 1, 5, help="Challenges in communication between different transport authorities.")
    
    compliance_strategies = st.multiselect("Select compliance strategies used", ["Dynamic Message Signs with Reason Codes", "Automated Enforcement Cameras", "Connected Vehicle Alerts", "Public Education Campaigns", "Other"], help="Choose methods used to improve driver compliance.")
    compliance_other = st.text_input("Specify other compliance strategies") if "Other" in compliance_strategies else ""
    
    st.header("📖 Section 5: Case Studies (80% Complete)")
    success_story = st.text_area("Describe a success story (Max 200 words)", max_chars=2000, help="Share a positive implementation example.")
    unexpected_challenges = st.text_area("Describe unexpected challenges faced (Max 150 words)", max_chars=1500, help="Share an issue that arose unexpectedly.")
    
    st.file_uploader("Attach any relevant case study reports (PDF, DOCX, or images)", type=["pdf", "docx", "png", "jpg", "jpeg"], help="Optional: Upload a case study report or supporting materials.")
    
    st.header("🔮 Section 6: Future Trends (90% Complete)")
    st.write("### Rank emerging technologies by potential impact on VSL systems (1 = Most Important, 4 = Least Important)")
    technology_impact = {
        "AI-Driven Predictive Analytics": st.number_input("AI-Driven Predictive Analytics", 1, 4, help="Use of AI to optimize VSL decisions."),
        "Satellite-Connected IoT Sensors": st.number_input("Satellite-Connected IoT Sensors", 1, 4, help="Using space-based technology for data collection."),
        "Autonomous Vehicle Integration": st.number_input("Autonomous Vehicle Integration", 1, 4, help="How self-driving cars will affect VSL."),
        "Blockchain Security Systems": st.number_input("Blockchain Security Systems", 1, 4, help="Improving security in data transactions.")
    }
    
    research_needs = st.multiselect("Select 2 urgent research needs", ["Climate Resilience Standards", "Cross-Cultural Compliance Factors", "Rural Implementation Frameworks", "Performance Metric Standardization"], help="Choose two key areas requiring more research.")

    st.header("🏢 Section 7: Optional Demographics")
    organization_type = st.selectbox("Organization Type", ["Government", "Private", "Academic", "NGO", "Other"], help="Select the type of organization you work for.")
    organization_other = st.text_input("Specify other organization type") if organization_type == "Other" else ""
    
    contact_permission = st.radio("May we contact you for follow-up?", ["Yes", "No"], help="Indicate if you’re open to follow-up questions.")
    email = st.text_input("Enter your email") if contact_permission == "Yes" else ""

    submitted = st.form_submit_button("✅ Submit")
    if submitted:
        response_data = { ... }
        save_response(response_data)
        st.success("Thank you for participating in the survey!")