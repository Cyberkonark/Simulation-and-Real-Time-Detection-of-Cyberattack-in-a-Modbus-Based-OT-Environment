import csv
import os
from datetime import datetime

RESPONSE_LOG = "ot_response_log.csv"


def get_recommendations(event_type):

    recommendations = {
        "UNAUTHORIZED_MODBUS_WRITE": [
            "Investigate the source IP address.",
            "Verify whether the Modbus write was authorized.",
            "Restrict unauthorized access to the Modbus service.",
            "Review affected PLC registers."
        ],

        "HIGH_CONNECTION_FREQUENCY": [
            "Investigate repeated connection attempts.",
            "Check the source IP address.",
            "Review firewall and network access rules."
        ],

        "UNKNOWN_SOURCE_IP": [
            "Identify the unknown network device.",
            "Verify its authorization.",
            "Review network access controls."
        ],

        "LOW WATER LEVEL": [
            "Inspect the water-level sensor.",
            "Verify pump and valve operation.",
            "Check the process safety thresholds."
        ],

        "HIGH WATER LEVEL": [
            "Inspect the water-level sensor.",
            "Verify valve and pump operation.",
            "Check the process safety thresholds."
        ]
    }

    return recommendations.get(
        event_type,
        ["Investigate the event and review relevant security logs."]
    )

def process_security_event(event):

    event_type = (
        event.get("Alert Type")
        or event.get("Condition")
        or event.get("Event Type")
        or "UNKNOWN_EVENT"
    )

    recommendations = get_recommendations(event_type)

    return {
        "event_type": event_type,
        "severity": event.get("Severity", "UNKNOWN"),
        "recommendations": recommendations
    }

def log_response_action(event_type, action, status="PENDING"):

    file_exists = os.path.exists(RESPONSE_LOG)

    with open(RESPONSE_LOG, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists or os.path.getsize(RESPONSE_LOG) == 0:
            writer.writerow([
                "Timestamp",
                "Event Type",
                "Response Action",
                "Status"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            event_type,
            action,
            status
        ])

def update_response_status(timestamp, new_status):

    allowed_statuses = [
        "PENDING",
        "IN_PROGRESS",
        "COMPLETED"
    ]

    if new_status not in allowed_statuses:
        print("Invalid response status.")
        return False

    if not os.path.exists(RESPONSE_LOG):
        return False

    with open(RESPONSE_LOG, "r", newline="") as file:
        reader = csv.DictReader(file)
        records = list(reader)

    found = False

    for record in records:
        if record["Timestamp"] == timestamp:
            record["Status"] = new_status
            found = True

    if not found:
        print("Response action not found.")
        return False

    with open(RESPONSE_LOG, "w", newline="") as file:
        fieldnames = [
            "Timestamp",
            "Event Type",
            "Response Action",
            "Status"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return True

if __name__ == "__main__":

    event = "UNAUTHORIZED_MODBUS_WRITE"

    print("\n========== OT SECURITY RESPONSE ==========")
    print("Detected Event:", event)
    print("\nRecommended Actions:")

    recommendations = get_recommendations(event)

    for number, recommendation in enumerate(recommendations, 1):
        print(f"{number}. {recommendation}")

    print("\nLogging response action...")
    
    log_response_action(
    event,
    recommendations[0],
    "PENDING")
    
    print("Response action logged successfully.")


    print("\nUpdating response status...")
    with open(RESPONSE_LOG, "r", newline="") as file:
        records = list(csv.DictReader(file))

    if records:
        timestamp = records[-1]["Timestamp"]
        
        success = update_response_status(
        timestamp,
        "COMPLETED")

        if success:
            print("Response status updated to COMPLETED.")

    print("\n========== EVENT-DRIVEN RESPONSE TEST ==========")
    sample_event = {
    "Alert Type": "UNAUTHORIZED_MODBUS_WRITE",
    "Severity": "HIGH"}

    result = process_security_event(sample_event)

    print("Event:", result["event_type"])
    print("Severity:", result["severity"])
    print("\nGenerated Recommendations:")

    for number, recommendation in enumerate(
        result["recommendations"], 1):
        print(f"{number}. {recommendation}")