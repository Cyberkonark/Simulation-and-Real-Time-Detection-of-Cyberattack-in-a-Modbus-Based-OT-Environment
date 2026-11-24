
# import time
# from datetime import datetime
# import csv
# import os

# import pandas as pd
# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# from pymodbus.client import ModbusTcpClient

# from ot_security_engine import (
#     collect_security_events,
#     remove_duplicate_events,
#     filter_recent_events,
#     calculate_risk_score,
#     generate_incidents,
#     generate_incident_timeline,
#     save_incidents
# )
# from incident_manager import (
#     load_incidents,
#     update_incident_status
# )

# from response_manager import (
#     get_recommendations,
#     log_response_action,
#     update_response_status,
#     process_security_event
# )
# from digital_twin import compare_process_state, save_twin_record

# # ---------------- CONFIGURATION ----------------

# MODBUS_HOST = "127.0.0.1"
# MODBUS_PORT = 5020
# DEVICE_ID = 1

# # -------- PROCESS ANOMALY CSV LOG --------

# PROCESS_LOG_FILE = "process_anomaly_log.csv"

# if not os.path.exists(PROCESS_LOG_FILE):
#     with open(PROCESS_LOG_FILE, "w", newline="") as file:
#         writer = csv.writer(file)
#         writer.writerow([
#             "Timestamp",
#             "Condition",
#             "Severity",
#             "Water Level",
#             "PLC Status"
#         ])

# st.set_page_config(
#     page_title="OT Process Monitor",
#     page_icon="🏭",
#     layout="wide"
# )

# # ---------------- MODBUS CONNECTION ----------------

# @st.cache_resource
# def connect_modbus():
#     client = ModbusTcpClient(
#         MODBUS_HOST,
#         port=MODBUS_PORT,
#         timeout=3
#     )

#     client.connect()
#     return client

# # ---------------- DASHBOARD ----------------

# st.title("OT Process Monitoring Dashboard")
# st.caption(
#     "Physical Sensor Monitoring | Arduino Uno | "
#     "Python Soft PLC | Modbus TCP"
# )

# st_autorefresh(interval=1000, key="dashboard_refresh")

# if "history" not in st.session_state:
#     st.session_state.history = []

# if "process_alerts" not in st.session_state:
#     st.session_state.process_alerts = []

# if "water_level" not in st.session_state:
#     st.session_state.water_level = None

# if "temperature" not in st.session_state:
#     st.session_state.temperature = None

# if "process_status" not in st.session_state:
#     st.session_state.process_status = None

# if "last_update" not in st.session_state:
#     st.session_state.last_update = "Waiting for data"

# if "modbus_log" not in st.session_state:
#     st.session_state.modbus_log = []

# # ---------------- READ MODBUS REGISTERS ----------------

# try:
#     client = connect_modbus()

#     if not client.connected:
#         if not client.connect():
#             raise ConnectionError("Could not connect to Modbus TCP server.")

#     result = client.read_holding_registers(
#         address=0,
#         count=3,
#         device_id=DEVICE_ID
#     )

#     if result.isError():
#         st.error(f"Modbus register read error: {result}")

#     else:
#         registers = result.registers

#         water = registers[0] / 10
#         temperature = registers[1] / 10
#         status = registers[2]

#         st.session_state.water_level = water
#         st.session_state.temperature = temperature
#         st.session_state.process_status = status

#         st.session_state.last_update = datetime.now().strftime(
#             "%H:%M:%S"
#         )

#         st.session_state.history.append({
#             "Time": st.session_state.last_update,
#             "Water Level (%)": water,
#             "Temperature (C)": temperature
#         })

#         # Record Modbus register activity
#         st.session_state.modbus_log.append({
#             "Time": st.session_state.last_update,
#             "HR0 - Water Level": registers[0],
#             "HR1 - Temperature": registers[1],
#             "HR2 - Process Status": registers[2]
#         })
        
#         # Keep the latest 100 records
#         st.session_state.modbus_log = (
#             st.session_state.modbus_log[-100:]
#         )

#         st.session_state.history = (
#             st.session_state.history[-60:]
#         )

#         st.success(
#             f"Connected to Modbus TCP at "
#             f"{MODBUS_HOST}:{MODBUS_PORT}"
#         )

# except Exception as error:
#     st.error(f"Modbus connection error: {error}")

# # ---------------- SENSOR DISPLAY ----------------

# col1, col2 = st.columns(2)

# with col1:
#     st.metric(
#         "Water Level",
#         f"{st.session_state.water_level:.1f}%"
#         if st.session_state.water_level is not None
#         else "Waiting..."
#     )

# with col2:
#     st.metric(
#         "LM35 Temperature",
#         f"{st.session_state.temperature:.1f} °C"
#         if st.session_state.temperature is not None
#         else "Waiting..."
#     )

# st.write("Last sensor update:", st.session_state.last_update)

# # ---------------- PROCESS MONITOR ----------------



# st.subheader("Process Monitor")

# water = st.session_state.water_level
# process_status = st.session_state.process_status

# if water is None or process_status is None:
#     st.warning("Waiting for process sensor data...")

# else:
#     if water < 30:
#         expected_status = 1
#         condition = "LOW WATER LEVEL"
#         severity = "MEDIUM"

#     elif water > 85:
#         expected_status = 2
#         condition = "HIGH WATER LEVEL"
#         severity = "HIGH"

#     else:
#         expected_status = 0
#         condition = "NORMAL"
#         severity = "INFO"

#     if process_status != expected_status:
#         condition = "PROCESS STATUS MISMATCH"
#         severity = "HIGH"

#     if condition == "NORMAL":
#         st.success("NORMAL PROCESS CONDITION")

#     else:
#         st.error(condition)

#         # Record only new anomaly events
        
# if condition != st.session_state.get("last_process_condition"):

#     event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # Store event in dashboard history
#     st.session_state.process_alerts.append({
#         "Time": event_time,
#         "Condition": condition,
#         "Severity": severity,
#         "Water Level": round(water, 1),
#         "PLC Status": process_status
#     })

#     st.session_state.process_alerts = (
#         st.session_state.process_alerts[-100:]
#     )

#     # Permanently save event to CSV
#     with open(PROCESS_LOG_FILE, "a", newline="") as file:
#         writer = csv.writer(file)

#         writer.writerow([
#             event_time,
#             condition,
#             severity,
#             round(water, 1),
#             process_status
#         ])


#     st.session_state.last_process_condition = condition

#     st.write(f"Water Level: {water:.1f}%")
#     st.write(f"PLC Process Status: {process_status}")

# # ---------------- Anomaly HISTORY ----------------


# st.divider()

# st.subheader("Process Anomaly History")

# if st.session_state.process_alerts:

#     process_alert_df = pd.DataFrame(
#         st.session_state.process_alerts
#     )

#     st.dataframe(
#         process_alert_df,
#         use_container_width=True,
#         hide_index=True
#     )

#     st.caption(
#         f"Total process anomalies recorded: "
#         f"{len(st.session_state.process_alerts)}"
#     )

# else:
#     st.info("No process anomalies detected yet.")
# # ---------------- SENSOR HISTORY ----------------

# st.subheader("Live Process Trends")

# if st.session_state.history:
#     df = pd.DataFrame(st.session_state.history)

#     st.line_chart(
#         df.set_index("Time")[
#             ["Water Level (%)", "Temperature (C)"]
#         ]
#     )
# else:
#     st.info("Waiting for valid Modbus sensor readings...")

# # ---------------- PROCESS STATUS ----------------

# st.subheader("Modbus Process Status")

# status = st.session_state.process_status

# if status == 0:
#     st.success("PLC Status: NORMAL")
# elif status == 1:
#     st.warning("PLC Status: LOW WATER LEVEL")
# elif status == 2:
#     st.error("PLC Status: HIGH WATER LEVEL")
# elif status is not None:
#     st.warning(f"Unknown PLC status: {status}")

# # Process condition and severity

# if status == 0:
#     condition = "NORMAL"
#     severity = "INFO"
# elif status == 1:
#     condition = "LOW WATER LEVEL"
#     severity = "MEDIUM"
# elif status == 2:
#     condition = "HIGH WATER LEVEL"
#     severity = "HIGH"
# else:
#     condition = "UNKNOWN"
#     severity = "LOW"
# st.caption("Data source: Arduino → Python Soft PLC → Modbus TCP")


# # ---------------- MODBUS MONITOR ----------------

# st.divider()

# st.header("Modbus TCP Monitor")

# st.write("Live Holding Register Activity")

# if st.session_state.modbus_log:

#     modbus_df = pd.DataFrame(
#         st.session_state.modbus_log
#     )

#     st.dataframe(
#         modbus_df.tail(20),
#         use_container_width=True,
#         hide_index=True
#     )

#     st.caption(
#         f"Total records captured: "
#         f"{len(st.session_state.modbus_log)}"
#     )

# else:
#     st.info("Waiting for Modbus register activity...")


# # =====================================
# # OT SECURITY ENGINE DASHBOARD
# # =====================================

# # 1. OT Security Engine heading
# st.divider()
# st.header("OT Security Engine")


# # 2. Collect security events
# security_events = collect_security_events()

# security_events = remove_duplicate_events(security_events)
# security_events = filter_recent_events(security_events)

# risk_score = calculate_risk_score(security_events)
# incidents = generate_incidents(security_events)
# save_incidents(incidents)
# timeline = generate_incident_timeline(security_events)


# # 3. Security Risk Assessment
# if risk_score >= 75:
#     risk_level = "CRITICAL"
# elif risk_score >= 50:
#     risk_level = "HIGH"
# elif risk_score >= 25:
#     risk_level = "MEDIUM"
# else:
#     risk_level = "LOW"

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.metric("Risk Score", f"{risk_score}/100")

# with col2:
#     st.metric("Risk Level", risk_level)

# with col3:
#     st.metric("Recent Events", len(security_events))


# # Security Event Severity Distribution

# st.divider()
# st.subheader("Security Event Severity Distribution")

# severity_counts = {
#     severity: sum(
#         1 for event in security_events
#         if event.get("Severity", "INFO").upper() == severity
#     )
#     for severity in ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
# }

# cols = st.columns(5)

# for col, severity in zip(cols, severity_counts):

#     with col:
#         st.metric(
#             severity,
#             severity_counts[severity]
#         )


# # -------- SECURITY RECOMMENDATIONS --------

# st.divider()
# st.subheader("Automated Security Recommendations")

# recommendations = []

# for event in security_events:

#     alert_type = event.get("Alert Type", "")
#     condition = event.get("Condition", "")
#     severity = event.get("Severity", "INFO").upper()

#     if alert_type in (
#         "UNAUTHORIZED_MODBUS_WRITE",
#         "MODBUS_WRITE_REQUEST"
#     ):
#         recommendations.append(
#             "Verify the Modbus write request and confirm that "
#             "the source IP is authorized."
#         )

#     if alert_type == "HIGH_CONNECTION_FREQUENCY":
#         recommendations.append(
#             "Investigate repeated TCP connection attempts "
#             "and verify the source device."
#         )

#     if condition == "LOW WATER LEVEL":
#         recommendations.append(
#             "Check the physical tank level and verify the "
#             "PLC process status."
#         )

#     if condition == "HIGH WATER LEVEL":
#         recommendations.append(
#             "Inspect the tank level and verify pump and valve operation."
#         )

#     if severity in ("HIGH", "CRITICAL"):
#         recommendations.append(
#             "Prioritize investigation of this high-severity security event."
#         )

# recommendations = list(dict.fromkeys(recommendations))

# if recommendations:

#     for recommendation in recommendations:
#         st.warning(recommendation)

# else:
#     st.success("No immediate security recommendations.")

# # 4. ADD OPEN INCIDENTS HERE

# st.divider()
# st.subheader("Open Security Incidents")

# if incidents:

#     incident_df = pd.DataFrame(incidents)

#     st.dataframe(
#         incident_df,
#         use_container_width=True,
#         hide_index=True
#     )

#     st.caption(f"Total open incidents: {len(incidents)}")

# else:

#     st.success("No high-severity security incidents detected.")

# # 5. Incident Timeline

# st.divider()
# st.subheader("Security Incident Timeline")

# if timeline:

#     timeline_df = pd.DataFrame(timeline)

#     st.dataframe(
#         timeline_df,
#         use_container_width=True,
#         hide_index=True
#     )

#     st.caption(
#         f"Total recent security events: {len(timeline)}"
#     )

# else:

#     st.info("No recent security events available.")



# #----Incident Lifecycle Management

# st.divider()
# st.header("Incident Lifecycle Management")

# managed_incidents = load_incidents()

# if managed_incidents:

#     st.subheader("Incident Records")

#     st.dataframe(
#         managed_incidents,
#         use_container_width=True
#     )

#     incident_options = list(range(len(managed_incidents)))

#     selected_index = st.selectbox(
#         "Select an incident",
#         incident_options,
#         format_func=lambda i: (
#             f"{managed_incidents[i]['Timestamp']} | "
#             f"{managed_incidents[i]['Severity']} | "
#             f"{managed_incidents[i]['Status']}"
#         )
#     )

#     selected_incident = managed_incidents[selected_index]

#     status_options = [
#         "OPEN",
#         "INVESTIGATING",
#         "RESOLVED"
#     ]

#     current_status = selected_incident["Status"]

#     selected_status = st.selectbox(
#         "Update incident status",
#         status_options,
#         index=status_options.index(current_status)
#     )

#     if st.button("Update Incident Status"):

#         success = update_incident_status(
#             selected_incident["Timestamp"],
#             selected_status
#         )

#         if success:
#             st.success("Incident status updated successfully.")
#             st.rerun()

# else:
#     st.info("No incidents available.")


# #---OT Security Response Management

# st.divider()
# st.header("OT Security Response Management")

# response_file = "ot_response_log.csv"

# if os.path.exists(response_file):

#     response_df = pd.read_csv(response_file)

#     st.subheader("Response Action History")

#     st.dataframe(
#         response_df,
#         use_container_width=True
#     )

#     if not response_df.empty:

#         st.subheader("Update Response Status")

#         response_index = st.selectbox(
#             "Select response action",
#             range(len(response_df)),
#             format_func=lambda i: (
#                 f"{response_df.iloc[i]['Timestamp']} | "
#                 f"{response_df.iloc[i]['Event Type']} | "
#                 f"{response_df.iloc[i]['Status']}"
#             ),
#             key="response_selection"
#         )

#         selected_response = response_df.iloc[response_index]

#         response_statuses = [
#             "PENDING",
#             "IN_PROGRESS",
#             "COMPLETED"
#         ]

#         new_response_status = st.selectbox(
#             "Response status",
#             response_statuses,
#             index=response_statuses.index(
#                 selected_response["Status"]
#             ),
#             key="response_status_selection"
#         )

#         if st.button("Update Response Action"):

#             success = update_response_status(
#                 selected_response["Timestamp"],
#                 new_response_status
#             )

#             if success:
#                 st.success("Response status updated.")
#                 st.rerun()

# else:
#     st.info("No response actions recorded yet.")


# #--Event-Driven Security Recommendations
# st.divider()
# st.header("Event-Driven Security Recommendations")

# if security_events:

#     grouped_events = {}

#     for event in security_events:

#         result = process_security_event(event)

#         key = (
#             result["event_type"],
#             result["severity"]
#         )

#         if key not in grouped_events:
#             grouped_events[key] = {
#                 "result": result,
#                 "count": 0
#             }

#         grouped_events[key]["count"] += 1

#     for index, (key, group) in enumerate(grouped_events.items()):

#         result = group["result"]

#         st.subheader(
#             f"{result['event_type']} — {result['severity']}"
#         )

#         st.caption(
#             f"Occurrences: {group['count']}"
#         )

#         st.write("Recommended response actions:")

#         for number, recommendation in enumerate(
#             result["recommendations"], 1
#         ):
#             st.write(f"{number}. {recommendation}")

#         selected_action = st.selectbox(
#             "Select response action to log",
#             result["recommendations"],
#             key=f"action_{index}"
#         )

#         if st.button(
#             "Log Response Action",
#             key=f"log_action_{index}"
#         ):

#             log_response_action(
#                 result["event_type"],
#                 selected_action,
#                 "PENDING"
#             )

#             st.success("Response action logged as PENDING.")

# else:
#     st.info("No recent security events available.")

# #--Digital Twin Monitoring


# st.divider()
# st.header("Digital Twin Monitoring")

# water = float(st.session_state.water_level)
# temperature = float(st.session_state.temperature)
# plc_status = int(st.session_state.process_status)

# twin_result = compare_process_state(
#     water,
#     temperature,
#     plc_status
# )

# if twin_result["Deviation"]:

#     st.warning(
#         "OT SECURITY ALERT: Digital Twin detected "
#         "a process-state mismatch."
#     )

# col1, col2 = st.columns(2)

# with col1:
#     st.metric(
#         "Expected Process State",
#         twin_result["Expected State"]
#     )

# with col2:
#     st.metric(
#         "Actual Process State",
#         twin_result["Actual State"]
#     )

# if twin_result["Deviation"]:
#     st.error("DIGITAL TWIN ALERT: Process state mismatch detected!")
# else:
#     st.success("Digital Twin: Process states match.")

# # Save only when the process state changes
# signature = (
#     twin_result["Expected State"],
#     twin_result["Actual State"],
#     twin_result["Deviation"]
# )

# if st.session_state.get("last_twin_signature") != signature:
#     save_twin_record(twin_result)
#     st.session_state.last_twin_signature = signature





import os
import csv
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from pymodbus.client import ModbusTcpClient

from ot_security_engine import (
    collect_security_events,
    remove_duplicate_events,
    filter_recent_events,
    calculate_risk_score,
    generate_incidents,
    generate_incident_timeline,
    save_incidents
)

from incident_manager import (
    load_incidents,
    update_incident_status
)

from response_manager import (
    log_response_action,
    update_response_status,
    process_security_event
)

from digital_twin import (
    compare_process_state,
    save_twin_record
)


# =========================================================
# CONFIGURATION
# =========================================================

MODBUS_HOST = "127.0.0.1"
MODBUS_PORT = 5020
DEVICE_ID = 1

PROCESS_LOG_FILE = "process_anomaly_log.csv"
RESPONSE_FILE = "ot_response_log.csv"
TWIN_FILE = "digital_twin_log.csv"

st.set_page_config(
    page_title="OT Security Command Center",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# FUTURISTIC UI DESIGN
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, #142b46 0%, transparent 32%),
        radial-gradient(circle at 95% 10%, #102d3b 0%, transparent 25%),
        #080e19;
    color: #e5edf8;
}

.block-container {
    max-width: 1600px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101d30, #0b1422);
    border-right: 1px solid #243850;
}

[data-testid="stSidebar"] * {
    color: #d8e5f4;
}

h1, h2, h3 {
    color: #f0f7ff !important;
    font-weight: 700 !important;
}

p, label {
    color: #b9c9dc;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #172a40, #101c2e);
    border: 1px solid #29435f;
    border-radius: 15px;
    padding: 18px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.20);
}

[data-testid="stMetricLabel"] {
    color: #9fb6cf !important;
    font-size: 13px !important;
}

[data-testid="stMetricValue"] {
    color: #55d6ff !important;
    font-weight: 800 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #29435f;
    border-radius: 12px;
}

.stButton > button {
    background: linear-gradient(90deg, #087da3, #0e7490);
    border: 1px solid #2696b9;
    color: white;
    border-radius: 9px;
    font-weight: 600;
    min-height: 40px;
}

.stButton > button:hover {
    background: #0e9bc2;
    border-color: #55d6ff;
    color: white;
}

div[data-testid="stSelectbox"] > div > div {
    background: #14243a;
}

hr {
    border-color: #263b55;
}

div[data-testid="stExpander"] {
    background: #111f32;
    border: 1px solid #29435f;
    border-radius: 12px;
}

.hero {
    background: linear-gradient(110deg, #132943, #12394b, #14243b);
    border: 1px solid #285574;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 22px;
    box-shadow: 0 10px 35px rgba(0,0,0,.2);
}

.hero-tag {
    color: #50d7ff;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 3px;
}

.hero-title {
    color: #ffffff;
    font-size: 29px;
    font-weight: 800;
    margin-top: 8px;
}

.hero-subtitle {
    color: #a9c1d8;
    font-size: 13px;
    margin-top: 8px;
}

.panel {
    background: linear-gradient(145deg, #15273c, #101c2d);
    border: 1px solid #29435f;
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 12px;
}

.panel-title {
    color: #58d5ff;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}

.panel-value {
    color: #f1f7ff;
    font-size: 23px;
    font-weight: 800;
}

.panel-description {
    color: #9cb2c9;
    font-size: 12px;
}

.green {
    color: #4ade80;
}

.red {
    color: #fb7185;
}

.orange {
    color: #fbbf24;
}

.cyan {
    color: #55d6ff;
}

.footer {
    color: #71869e;
    text-align: center;
    padding: 18px;
    font-size: 11px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "history": [],
    "process_alerts": [],
    "modbus_log": [],
    "water_level": None,
    "temperature": None,
    "process_status": None,
    "last_update": "Waiting for data",
    "last_process_condition": None,
    "last_twin_signature": None,
    "modbus_connected": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# MODBUS CONNECTION
# =========================================================

@st.cache_resource
def connect_modbus():
    client = ModbusTcpClient(
        MODBUS_HOST,
        port=MODBUS_PORT,
        timeout=3
    )
    client.connect()
    return client


# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(
    interval=2000,
    key="ot_refresh"
)


# =========================================================
# READ PLC DATA
# =========================================================

try:

    client = connect_modbus()

    if not client.connected:
        if not client.connect():
            raise ConnectionError("Modbus connection failed")

    result = client.read_holding_registers(
        address=0,
        count=3,
        device_id=DEVICE_ID
    )

    if result.isError():
        raise ConnectionError(str(result))

    registers = result.registers

    water = registers[0] / 10
    temperature = registers[1] / 10
    status = registers[2]

    st.session_state.water_level = water
    st.session_state.temperature = temperature
    st.session_state.process_status = status
    st.session_state.modbus_connected = True

    timestamp = datetime.now().strftime("%H:%M:%S")

    st.session_state.last_update = timestamp

    st.session_state.history.append({
        "Time": timestamp,
        "Water Level (%)": water,
        "Temperature (C)": temperature
    })

    st.session_state.history = (
        st.session_state.history[-60:]
    )

    st.session_state.modbus_log.append({
        "Time": timestamp,
        "HR0 - Water Level": registers[0],
        "HR1 - Temperature": registers[1],
        "HR2 - Process Status": registers[2]
    })

    st.session_state.modbus_log = (
        st.session_state.modbus_log[-100:]
    )

except Exception as error:

    st.session_state.modbus_connected = False
    st.sidebar.error(f"Modbus connection error: {error}")


# =========================================================
# PROCESS VALIDATION
# =========================================================

water = st.session_state.water_level
temperature = st.session_state.temperature
process_status = st.session_state.process_status

condition = "UNKNOWN"
severity = "LOW"

if water is not None and process_status is not None:

    if water < 30:
        expected_status = 1
        condition = "LOW WATER LEVEL"
        severity = "MEDIUM"

    elif water > 85:
        expected_status = 2
        condition = "HIGH WATER LEVEL"
        severity = "HIGH"

    else:
        expected_status = 0
        condition = "NORMAL"
        severity = "INFO"

    if process_status != expected_status:
        condition = "PROCESS STATUS MISMATCH"
        severity = "HIGH"

    if condition != st.session_state.last_process_condition:

        event_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        st.session_state.process_alerts.append({
            "Time": event_time,
            "Condition": condition,
            "Severity": severity,
            "Water Level": round(water, 1),
            "PLC Status": process_status
        })

        st.session_state.process_alerts = (
            st.session_state.process_alerts[-100:]
        )

        with open(PROCESS_LOG_FILE, "a", newline="") as file:
            writer = csv.writer(file)

            writer.writerow([
                event_time,
                condition,
                severity,
                round(water, 1),
                process_status
            ])

        st.session_state.last_process_condition = condition


# =========================================================
# SECURITY ENGINE
# =========================================================

security_events = collect_security_events()

security_events = remove_duplicate_events(security_events)
security_events = filter_recent_events(security_events)

risk_score = calculate_risk_score(security_events)

incidents = generate_incidents(security_events)

save_incidents(incidents)

timeline = generate_incident_timeline(security_events)

risk_level = (
    "CRITICAL" if risk_score >= 75 else
    "HIGH" if risk_score >= 50 else
    "MEDIUM" if risk_score >= 25 else
    "LOW"
)

critical_count = sum(
    1 for e in security_events
    if e.get("Severity", "").upper() == "CRITICAL"
)

high_count = sum(
    1 for e in security_events
    if e.get("Severity", "").upper() == "HIGH"
)

mitm_events = [
    e for e in security_events
    if "MODBUS_SETPOINT_INJECTION" in str(e)
]


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <div class="hero-tag">INDUSTRIAL CYBER DEFENSE PLATFORM</div>
    <div class="hero-title">OT SECURITY COMMAND CENTER</div>
    <div class="hero-subtitle">
        REAL-TIME PROCESS MONITORING
        &nbsp; | &nbsp; MODBUS TCP
        &nbsp; | &nbsp; MITM DETECTION
        &nbsp; | &nbsp; DIGITAL TWIN
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("# 🏭 OT COMMAND")
st.sidebar.caption("SECURITY OPERATIONS PLATFORM")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Command Center",
        "Process Monitoring",
        "Network Intelligence",
        "Incident Management",
        "Response Center",
        "Digital Twin"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### SYSTEM STATUS")

if st.session_state.modbus_connected:
    st.sidebar.success("PLC ONLINE")
else:
    st.sidebar.error("PLC OFFLINE")

st.sidebar.caption("Arduino Uno")
st.sidebar.caption("Python Soft PLC")
st.sidebar.caption("Modbus TCP : 5020")
st.sidebar.caption("MITM Proxy : 15020")

st.sidebar.divider()

st.sidebar.caption(
    f"Last update: {st.session_state.last_update}"
)


# =========================================================
# COMMAND CENTER
# =========================================================

if page == "Command Center":

    st.subheader("COMMAND CENTER OVERVIEW")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "WATER LEVEL",
            f"{water:.1f}%" if water is not None else "N/A"
        )

    with c2:
        st.metric(
            "TEMPERATURE",
            f"{temperature:.1f} °C"
            if temperature is not None else "N/A"
        )

    with c3:
        st.metric(
            "SECURITY RISK",
            f"{risk_score}/100",
            risk_level
        )

    with c4:
        st.metric(
            "SECURITY EVENTS",
            len(security_events)
        )

    st.divider()

    left, right = st.columns([1.2, 1])

    with left:

        st.markdown("### INDUSTRIAL PROCESS")

        st.markdown("""
        <div class="panel">
            <div class="panel-title">OT PROCESS ARCHITECTURE</div>
            <div style="display:flex;justify-content:space-around;
            align-items:center;text-align:center;gap:5px;">
                <div>
                    <div style="font-size:30px;">📡</div>
                    <b>ARDUINO</b>
                    <div class="panel-description">Sensors</div>
                </div>
                <div class="cyan">➜</div>
                <div>
                    <div style="font-size:30px;">⚙️</div>
                    <b>SOFT PLC</b>
                    <div class="panel-description">Controller</div>
                </div>
                <div class="cyan">➜</div>
                <div>
                    <div style="font-size:30px;">🔗</div>
                    <b>MODBUS</b>
                    <div class="panel-description">TCP</div>
                </div>
                <div class="cyan">➜</div>
                <div>
                    <div style="font-size:30px;">🛡️</div>
                    <b>SECURITY</b>
                    <div class="panel-description">Engine</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if condition == "NORMAL":
            st.success("PROCESS CONDITION: NORMAL")
        elif condition != "UNKNOWN":
            st.error(f"PROCESS CONDITION: {condition}")
        else:
            st.warning("Waiting for process data")

    with right:

        st.markdown("### CYBERSECURITY STATUS")

        if risk_level == "CRITICAL":
            st.error("CRITICAL SECURITY RISK")
        elif risk_level == "HIGH":
            st.warning("HIGH SECURITY RISK")
        elif risk_level == "MEDIUM":
            st.warning("MEDIUM SECURITY RISK")
        else:
            st.success("LOW SECURITY RISK")

        st.write(f"Critical alerts: {critical_count}")
        st.write(f"High severity alerts: {high_count}")
        st.write(f"MITM events: {len(mitm_events)}")

        if mitm_events:
            st.error("MODBUS SETPOINT INJECTION DETECTED")
        else:
            st.success("No recent MITM alerts")

    st.divider()

    st.markdown("### LIVE SENSOR INTELLIGENCE")

    if st.session_state.history:

        history_df = pd.DataFrame(st.session_state.history)

        st.line_chart(
            history_df.set_index("Time"),
            height=280
        )

    else:
        st.info("Waiting for sensor data")

    st.markdown("### RECENT SECURITY EVENTS")

    if security_events:

        st.dataframe(
            pd.DataFrame(security_events).tail(10),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success("No recent security events")


# =========================================================
# PROCESS MONITORING
# =========================================================

elif page == "Process Monitoring":

    st.subheader("INDUSTRIAL PROCESS MONITORING")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "WATER LEVEL",
            f"{water:.1f}%" if water is not None else "N/A"
        )

    with c2:
        st.metric(
            "LM35 TEMPERATURE",
            f"{temperature:.1f} °C"
            if temperature is not None else "N/A"
        )

    with c3:
        st.metric(
            "PLC STATUS",
            str(process_status)
            if process_status is not None else "N/A"
        )

    st.divider()

    if condition == "NORMAL":
        st.success("NORMAL PROCESS CONDITION")
    elif condition != "UNKNOWN":
        st.error(condition)
    else:
        st.warning("Waiting for process data")

    st.markdown("### SENSOR TRENDS")

    if st.session_state.history:

        df = pd.DataFrame(st.session_state.history)

        st.line_chart(
            df.set_index("Time"),
            height=350
        )

    st.markdown("### PROCESS ANOMALY HISTORY")

    if st.session_state.process_alerts:

        st.dataframe(
            pd.DataFrame(st.session_state.process_alerts),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success("No process anomalies recorded")

    st.markdown("### MODBUS HOLDING REGISTERS")

    if st.session_state.modbus_log:

        st.dataframe(
            pd.DataFrame(st.session_state.modbus_log).tail(20),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Waiting for Modbus activity")


# =========================================================
# NETWORK INTELLIGENCE
# =========================================================

elif page == "Network Intelligence":

    st.subheader("NETWORK INTELLIGENCE CENTER")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("RISK SCORE", f"{risk_score}/100")

    with c2:
        st.metric("CRITICAL EVENTS", critical_count)

    with c3:
        st.metric("MITM EVENTS", len(mitm_events))

    st.divider()

    st.markdown("### SECURITY SEVERITY DISTRIBUTION")

    severities = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

    counts = {
        s: sum(
            1 for e in security_events
            if e.get("Severity", "INFO").upper() == s
        )
        for s in severities
    }

    cols = st.columns(5)

    for col, severity in zip(cols, severities):
        with col:
            st.metric(severity, counts[severity])

    st.divider()

    st.markdown("### LIVE SECURITY EVENT FEED")

    if security_events:

        st.dataframe(
            pd.DataFrame(security_events),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success("No recent security events")

    st.markdown("### MITM INJECTION MONITOR")

    if mitm_events:

        st.error("MODBUS SETPOINT INJECTION DETECTED")

        st.dataframe(
            pd.DataFrame(mitm_events),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success("No recent MITM injection events")

    st.caption(
        "The configured MITM test protects HR10. "
        "It is not a claim of universal MITM prevention."
    )


# =========================================================
# INCIDENT MANAGEMENT
# =========================================================

elif page == "Incident Management":

    st.subheader("INCIDENT LIFECYCLE MANAGEMENT")

    managed_incidents = load_incidents()

    if managed_incidents:

        st.dataframe(
            pd.DataFrame(managed_incidents),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        index = st.selectbox(
            "Select incident",
            range(len(managed_incidents)),
            format_func=lambda i: (
                f"{managed_incidents[i]['Timestamp']} | "
                f"{managed_incidents[i]['Severity']} | "
                f"{managed_incidents[i]['Status']}"
            ),
            key="incident_selection"
        )

        selected = managed_incidents[index]

        statuses = [
            "OPEN",
            "INVESTIGATING",
            "RESOLVED"
        ]

        current = selected["Status"]

        new_status = st.selectbox(
            "Update incident status",
            statuses,
            index=statuses.index(current),
            key="incident_status"
        )

        if st.button("UPDATE INCIDENT"):

            success = update_incident_status(
                selected["Timestamp"],
                new_status
            )

            if success:
                st.success("Incident status updated")
                st.rerun()

    else:
        st.success("No incidents available")

    st.divider()

    st.markdown("### SECURITY TIMELINE")

    if timeline:

        st.dataframe(
            pd.DataFrame(timeline),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No recent security timeline records")


# =========================================================
# RESPONSE CENTER
# =========================================================

elif page == "Response Center":

    st.subheader("OT SECURITY RESPONSE CENTER")

    if os.path.exists(RESPONSE_FILE):

        response_df = pd.read_csv(RESPONSE_FILE)

        st.markdown("### RESPONSE ACTION HISTORY")

        st.dataframe(
            response_df,
            use_container_width=True,
            hide_index=True
        )

        if not response_df.empty:

            index = st.selectbox(
                "Select response action",
                range(len(response_df)),
                format_func=lambda i: (
                    f"{response_df.iloc[i]['Timestamp']} | "
                    f"{response_df.iloc[i]['Event Type']} | "
                    f"{response_df.iloc[i]['Status']}"
                ),
                key="response_selection"
            )

            selected = response_df.iloc[index]

            statuses = [
                "PENDING",
                "IN_PROGRESS",
                "COMPLETED"
            ]

            current = selected["Status"]

            new_status = st.selectbox(
                "Response status",
                statuses,
                index=statuses.index(current),
                key="response_status"
            )

            if st.button("UPDATE RESPONSE"):

                success = update_response_status(
                    selected["Timestamp"],
                    new_status
                )

                if success:
                    st.success("Response updated")
                    st.rerun()

    else:
        st.info("No response actions recorded")

    st.divider()

    st.markdown("### EVENT-DRIVEN SECURITY RECOMMENDATIONS")

    if security_events:

        grouped = {}

        for event in security_events:

            result = process_security_event(event)

            key = (
                result["event_type"],
                result["severity"]
            )

            if key not in grouped:
                grouped[key] = {
                    "result": result,
                    "count": 0
                }

            grouped[key]["count"] += 1

        for index, group in enumerate(grouped.values()):

            result = group["result"]

            with st.expander(
                f"{result['event_type']} | "
                f"{result['severity']} | "
                f"{group['count']} events"
            ):

                for number, action in enumerate(
                    result["recommendations"], 1
                ):
                    st.write(f"{number}. {action}")

                if result["recommendations"]:

                    action = st.selectbox(
                        "Choose response action",
                        result["recommendations"],
                        key=f"action_{index}"
                    )

                    if st.button(
                        "LOG RESPONSE",
                        key=f"log_{index}"
                    ):

                        log_response_action(
                            result["event_type"],
                            action,
                            "PENDING"
                        )

                        st.success("Response logged")


# =========================================================
# DIGITAL TWIN
# =========================================================

elif page == "Digital Twin":

    st.subheader("DIGITAL TWIN INTELLIGENCE")

    if (
        water is not None
        and temperature is not None
        and process_status is not None
    ):

        twin_result = compare_process_state(
            float(water),
            float(temperature),
            int(process_status)
        )

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "EXPECTED STATE",
                twin_result["Expected State"]
            )

        with c2:
            st.metric(
                "ACTUAL STATE",
                twin_result["Actual State"]
            )

        st.divider()

        if twin_result["Deviation"]:
            st.error("PROCESS DEVIATION DETECTED")
        else:
            st.success("PROCESS STATES MATCH")

        signature = (
            twin_result["Expected State"],
            twin_result["Actual State"],
            twin_result["Deviation"]
        )

        if st.session_state.last_twin_signature != signature:

            save_twin_record(twin_result)

            st.session_state.last_twin_signature = signature

    else:
        st.warning(
            "Digital Twin waiting for valid Modbus data"
        )

    st.divider()

    st.markdown("### DIGITAL TWIN HISTORY")

    if os.path.exists(TWIN_FILE):

        twin_df = pd.read_csv(TWIN_FILE)

        st.dataframe(
            twin_df.tail(30),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No Digital Twin history available")


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    OT SECURITY COMMAND CENTER
    <br><br>
    ARDUINO UNO | PYTHON SOFT PLC | MODBUS TCP |
    MITM DETECTION & PREVENTION | DIGITAL TWIN
</div>
""", unsafe_allow_html=True)
