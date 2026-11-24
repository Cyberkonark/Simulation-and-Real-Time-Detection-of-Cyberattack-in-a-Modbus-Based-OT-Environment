from ot_security_engine import (
    remove_duplicate_events,
    calculate_risk_score
)

events = [
    {
        "Timestamp": "2026-11-22 12:05:00",
        "Source": "NETWORK",
        "Source IP": "127.0.0.1",
        "Destination IP": "127.0.0.1",
        "Alert Type": "UNAUTHORIZED_MODBUS_WRITE",
        "Severity": "HIGH",
        "Description": "Write request | Operation: WRITE_MULTIPLE_REGISTERS"
    },
    {
        "Timestamp": "2026-11-22 12:06:00",
        "Source": "NETWORK",
        "Source IP": "127.0.0.1",
        "Destination IP": "127.0.0.1",
        "Alert Type": "UNAUTHORIZED_MODBUS_WRITE",
        "Severity": "HIGH",
        "Description": "Write request | Operation: WRITE_MULTIPLE_REGISTERS"
    }
]

result = remove_duplicate_events(events)

print("Original events:", len(events))
print("Events after deduplication:", len(result))

for event in result:
    print(
        event["Timestamp"],
        "|",
        event["Alert Type"],
        "|",
        event["Severity"]
    )


print("\n========== RISK SCORE TEST ==========")

test_events = [
    {"Severity": "HIGH"},
    {"Severity": "MEDIUM"},
    {"Severity": "LOW"}
]

score = calculate_risk_score(test_events)

print("Expected risk score: 50")
print("Actual risk score:", score)


from digital_twin import compare_process_state

print("\n========== DIGITAL TWIN TEST ==========")

test_result = compare_process_state(
    water=60,
    temperature=28,
    plc_status=1
)

print("Expected:", test_result["Expected State"])
print("Actual:", test_result["Actual State"])
print("Deviation:", test_result["Deviation"])