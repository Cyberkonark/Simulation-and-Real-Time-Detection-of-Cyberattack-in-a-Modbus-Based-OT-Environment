
from datetime import datetime
import csv
import os

TWIN_LOG = "digital_twin_log.csv"

# Expected operating limits
MIN_WATER_LEVEL = 30.0
MAX_WATER_LEVEL = 85.0

MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 60.0


def calculate_expected_status(water, temperature):

    if water < MIN_WATER_LEVEL:
        return "LOW WATER LEVEL"

    if water > MAX_WATER_LEVEL:
        return "HIGH WATER LEVEL"

    if not MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE:
        return "TEMPERATURE ANOMALY"

    return "NORMAL"


def compare_process_state(water, temperature, plc_status):

    expected_status = calculate_expected_status(
        water, temperature
    )

    actual_status = {
        0: "NORMAL",
        1: "LOW WATER LEVEL",
        2: "HIGH WATER LEVEL"
    }.get(plc_status, "UNKNOWN")

    deviation = expected_status != actual_status

    return {
        "Timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "Water Level": water,
        "Temperature": temperature,
        "Expected State": expected_status,
        "Actual State": actual_status,
        "Deviation": deviation
    }


def save_twin_record(record):

    file_exists = os.path.exists(TWIN_LOG)

    with open(TWIN_LOG, "a", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=record.keys()
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)
