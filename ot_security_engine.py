import csv
import os
from datetime import datetime, timedelta

PROCESS_LOG_FILE = "process_anomaly_log.csv"
NETWORK_ALERT_FILE = "network_alerts.csv"
INCIDENT_LOG_FILE = "ot_incident_log.csv"

def collect_security_events():

    events = []

    log_files = [
        (PROCESS_LOG_FILE, "PROCESS"),
        (NETWORK_ALERT_FILE, "NETWORK")
    ]

    for file_path, event_source in log_files:

        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, "r", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    row["Source"] = event_source
                    if "Event" in row:
                        row["Alert Type"] = row["Event"]
                    events.append(row)

        except Exception as error:
            print(f"Error reading {file_path}: {error}")

    return events

def remove_duplicate_events(events):

    unique_events = []
    seen_events = set()
    unauthorized_writes = set()

    # First identify unauthorized Modbus writes
    for event in events:

        if event.get("Alert Type") == "UNAUTHORIZED_MODBUS_WRITE":

            signature = (
                event.get("Timestamp"),
                event.get("Source IP"),
                event.get("Destination IP"),
                event.get("Description", "").split("Operation: ")[-1]
            )

            unauthorized_writes.add(signature)

    # Then process all events
    for event in events:

        if (
            event.get("Source") == "PROCESS"
            and event.get("Condition") == "NORMAL"
        ):
            continue

        alert_type = event.get("Alert Type", "")

        # Suppress generic alert if the same write
        # was already identified as unauthorized
        if alert_type == "MODBUS_WRITE_REQUEST":

            signature = (
                event.get("Timestamp"),
                event.get("Source IP"),
                event.get("Destination IP"),
                event.get("Description", "").split(
                    "detected: "
                )[-1]
            )

            if signature in unauthorized_writes:
                continue

        # Remove exact duplicate records
        event_key = tuple(sorted(event.items()))

        if event_key not in seen_events:
            seen_events.add(event_key)
            unique_events.append(event)

    return unique_events

def filter_recent_events(events):

    recent_events = []

    current_time = datetime.now()
    time_window = timedelta(minutes=15)

    for event in events:

        timestamp = event.get("Timestamp")

        try:
            event_time = datetime.strptime(
                timestamp,
                "%Y-%m-%d %H:%M:%S"
            )

            if current_time - time_window <= event_time <= current_time:
                recent_events.append(event)

        except (ValueError, TypeError):
            continue

    return recent_events

def generate_incidents(events):

    incidents = []

    for event in events:

        severity = event.get("Severity", "INFO").upper()

        if severity in ("HIGH", "CRITICAL"):

            incident = {
                "Timestamp": event.get("Timestamp"),
                "Source": event.get("Source"),
                "Severity": severity,
                "Description": event.get(
                    "Description",
                    event.get("Condition", "Security anomaly")
                ),
                "Status": "OPEN"
            }

            incidents.append(incident)

    return incidents

def save_incidents(incidents):

    fieldnames = [
        "Timestamp",
        "Source",
        "Severity",
        "Description",
        "Status"
    ]

    existing_ids = set()

    if os.path.exists(INCIDENT_LOG_FILE):

        with open(INCIDENT_LOG_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                incident_id = (
                    row["Timestamp"],
                    row["Source"],
                    row["Description"]
                )
                existing_ids.add(incident_id)

    with open(INCIDENT_LOG_FILE, "a", newline="") as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if os.path.getsize(INCIDENT_LOG_FILE) == 0:
            writer.writeheader()

        for incident in incidents:

            incident_id = (
                incident["Timestamp"],
                incident["Source"],
                incident["Description"]
            )

            if incident_id not in existing_ids:
                writer.writerow(incident)
                existing_ids.add(incident_id)

def generate_incident_timeline(events):

    timeline = []

    for event in events:

        entry = {
            "Timestamp": event.get("Timestamp"),
            "Source": event.get("Source"),
            "Event": event.get(
                "Alert Type",
                event.get("Condition", "Unknown Event")
            ),
            "Severity": event.get("Severity", "INFO")
        }

        timeline.append(entry)

    timeline.sort(
        key=lambda item: item["Timestamp"]
    )

    return timeline



def calculate_risk_score(events):

    severity_weights = {
        "INFO": 1,
        "LOW": 5,
        "MEDIUM": 15,
        "HIGH": 30,
        "CRITICAL": 50
    }

    risk_score = 0

    for event in events:

        severity = event.get("Severity", "INFO").upper()

        weight = severity_weights.get(severity, 0)

        risk_score += weight

    risk_score = min(risk_score, 100)

    return risk_score


if __name__ == "__main__":

    security_events = collect_security_events()
    
    security_events = remove_duplicate_events(security_events)

    security_events = filter_recent_events(security_events)

    risk_score = calculate_risk_score(security_events)

    incidents = generate_incidents(security_events)

    timeline = generate_incident_timeline(security_events)

    print("\n========== OT SECURITY INCIDENTS ==========")
    
    print("Total Open Incidents:", len(incidents))
    if incidents:
        for incident in incidents:
            print("\nIncident Details:")
            print("Timestamp:", incident["Timestamp"])
            print("Source:", incident["Source"])
            print("Severity:", incident["Severity"])
            print("Description:", incident["Description"])
            print("Status:", incident["Status"])

    else:
        print("No high-severity incidents detected.")

    print("\n========== OT SECURITY ENGINE ==========")

    print("Total security events:", len(security_events))

    print("OT Security Risk Score:", risk_score, "/ 100")

    if risk_score >= 75:
        print("Risk Level: CRITICAL")

    elif risk_score >= 50:
        print("Risk Level: HIGH")

    elif risk_score >= 25:
        print("Risk Level: MEDIUM")

    else:
        print("Risk Level: LOW")

    print("\n========== COLLECTED EVENTS ==========")

    for event in security_events:
        print(event)


    print("\n========== OT SECURITY EVENT TIMELINE ==========")
    
    for event in timeline:
        print(
            f"{event['Timestamp']} | "
            f"{event['Source']} | "
            f"{event['Event']} | "
            f"{event['Severity']}"
        )