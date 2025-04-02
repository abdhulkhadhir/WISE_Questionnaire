import streamlit as st
import pandas as pd
import os
import logging
from github import Github

# ---- GitHub Configuration ----
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "abdhulkhadhir/WISE_Questionnaire"
CSV_PATH = "responses.csv"

def save_to_github(df):
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file_content = df.to_csv(index=False)

        try:
            file = repo.get_contents(CSV_PATH)
            repo.update_file(CSV_PATH, "Update VSL responses file", file_content, file.sha)
            logging.info("File updated successfully")
        except Exception:
            repo.create_file(CSV_PATH, "Create VSL responses file", file_content)
            logging.info("File created successfully")
    except Exception as e:
        logging.error(f"Error in save_to_github function: {e}")

st.set_page_config(page_title="Weather-Responsive VSL Survey", layout="wide")
st.title("🌍 Weather-Responsive Variable Speed Limits (WRVSL) Survey")
st.write("**Purpose:** Identify global best practices and challenges in weather-responsive variable speed limit (VSL) implementations.")
st.write("**Ethics Approval:** ERB-2024-009 | All responses anonymized")
st.write("**Estimated Time:** 12–15 minutes")

with st.form("survey_form"):
    st.header("📝 Section 1: Consent and Introduction")
    consent = st.checkbox("I consent to participate in this anonymous study")
    data_use = st.checkbox("I agree to terms of data use for academic research")
    
    st.header("🌍 Section 2: Practitioner Background (15% Complete)")
    geographical_context = st.selectbox("In which country/region do you primarily work?", ["North America", "Europe", "Australia/NZ", "Asia", "Middle East", "Africa", "South America"], help="Select your primary region of professional work.")
    role = st.selectbox("Select your primary role", ["Traffic Operations Manager", "Transportation Engineer", "Policy Advisor", "Researcher/Academic", "Other"], help="Choose the role that best describes your profession.")
    role_other = st.text_input("Please specify your role") if role == "Other" else ""
    experience = st.selectbox("How many years have you worked with weather-responsive VSL implementations?", ["<1 year", "1–3 years", "4–7 years", "8+ years"], help="Select the range that best fits your experience.")

    st.header("⚙️ Section 3: VSL System Design (35% Complete)")
    weather_params = st.multiselect("Select the 3 most critical weather parameters influencing WRVSL", ["Visibility", "Precipitation intensity", "Pavement temperature", "Wind speed", "Road friction", "Humidity", "Other"], help="Choose up to three parameters that most impact WRVSL decisions.")
    weather_params_other = st.text_input("Specify other weather parameters") if "Other" in weather_params else ""
    
    st.write("### Rank data sources used for WRVSL decisions (1 = Most Important, 5 = Least Important)")
    data_sources = {
        "Roadside Weather Information System (RWIS)": st.number_input("RWIS", 1, 5, help="Fixed stations collecting real-time weather data."),
        "Connected Vehicle Telematics": st.number_input("Connected Vehicle Telematics", 1, 5, help="Data from vehicles equipped with sensors."),
        "CCTV/Thermal Cameras": st.number_input("CCTV/Thermal Cameras", 1, 5, help="Video-based monitoring systems."),
        "Weather Radar Forecasts": st.number_input("Weather Radar Forecasts", 1, 5, help="Predictive weather modeling."),
        "Manual Operator Input": st.number_input("Manual Operator Input", 1, 5, help="Decisions made by traffic control operators.")
    }
    
    verification_method = st.text_input("Do you have a verification method (e.g., cameras or alternative data sources) to verify inputs?")
    
    control_logic = st.selectbox("Which control logic does your system primarily use?", ["Rule-Based Thresholds", "Fuzzy Logic", "Machine Learning", "Model Predictive Control", "Hybrid Approach"], help="Select the method used to determine WRVSL adjustments.")
    
    mode_operation = st.selectbox("Mode of operation", ["Alert only", "System recommended response requiring operator approval", "Fully automated"], help="Specify how the WRVSL system is operated.")
    
    mode_deactivation = st.selectbox("Mode of deactivation", ["Manual removal", "Automated with operator alert", "Automated without alert"], help="Specify how WRVSL is deactivated.")
    
    st.header("⚠️ Section 4: Operational Challenges (60% Complete)")
    st.write("### Rate the significance of the following challenges in your WRVSL operations (1 = Not Significant, 5 = Critical)")
    driver_compliance = st.slider("Driver Compliance", 1, 5, help="How well do drivers adhere to WRVSL changes?")
    sensor_reliability = st.slider("Sensor Reliability", 1, 5, help="Issues with accuracy and functionality of sensors.")
    cybersecurity_risks = st.slider("Cybersecurity Risks", 1, 5, help="Concerns about hacking or data breaches.")
    multi_agency_coordination = st.slider("Multi-Agency Coordination", 1, 5, help="Challenges in communication between different transport authorities.")
    operational_resources = st.slider("Operational FTE / Optimization Resources", 1, 5, help="Availability of staff and resources for WRVSL optimization.")
    
    compliance_strategies = st.multiselect("Select compliance strategies used", ["Dynamic Message Signs with Reason Codes", "Automated Enforcement Cameras", "Connected Vehicle Alerts", "Public Education Campaigns", "Other"], help="Choose methods used to improve driver compliance.")
    compliance_other = st.text_input("Specify other compliance strategies") if "Other" in compliance_strategies else ""
    
    st.header("📖 Section 5: Case Studies (80% Complete)")
    success_story = st.text_area("Describe a success story (Max 200 words)", max_chars=2000, help="Share a positive implementation example.")
    unexpected_challenges = st.text_area("Describe unexpected challenges faced (Max 150 words)", max_chars=1500, help="Share an issue that arose unexpectedly.")
    
    geographic_coverage = st.text_input("Describe the geographic coverage of WRVSL (e.g., within 5km of sensors, entire carriageway, overlapping zones)")
    
    submitted = st.form_submit_button("✅ Submit")
    if submitted:
        df = pd.DataFrame([{ ... }])
        save_to_github(df)
        st.success("Thank you for participating in the survey!")
