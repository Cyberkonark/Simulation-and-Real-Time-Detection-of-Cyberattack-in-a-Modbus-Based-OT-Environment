import csv
import os

INCIDENT_FILE = "ot_incident_log.csv"


def load_incidents():

    if not os.path.exists(INCIDENT_FILE):
        return []

    with open(INCIDENT_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def update_incident_status(timestamp, new_status):

    allowed_statuses = [
        "OPEN",
        "INVESTIGATING",
        "RESOLVED"
    ]

    if new_status not in allowed_statuses:
        print("Invalid incident status.")
        return False

    incidents = load_incidents()
    found = False

    for incident in incidents:

        if incident["Timestamp"] == timestamp:
            incident["Status"] = new_status
            found = True

    if not found:
        print("Incident not found.")
        return False

    with open(INCIDENT_FILE, "w", newline="") as file:

        fieldnames = [
            "Timestamp",
            "Source",
            "Severity",
            "Description",
            "Status"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(incidents)

    return True


if __name__ == "__main__":

    incidents = load_incidents()

    print("\n========== INCIDENT MANAGEMENT ==========")
    print("Total incidents:", len(incidents))

    for incident in incidents:
        print(
            incident["Timestamp"],
            "|",
            incident["Severity"],
            "|",
            incident["Status"],
            "|",
            incident["Description"]
        )

