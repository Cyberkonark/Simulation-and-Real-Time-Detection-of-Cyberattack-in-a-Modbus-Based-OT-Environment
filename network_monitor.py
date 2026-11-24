
from scapy.all import sniff, IP, TCP, Raw
from datetime import datetime
from collections import defaultdict, deque
import csv
import os
import time

# ---------------- CONFIGURATION ----------------

INTERFACE = r"\Device\NPF_{0FB6F655-59AA-4112-99A2-CE527B0DAC69}"
MODBUS_PORT = 5020
LOG_FILE = "network_traffic.csv"

# ---------------- ANOMALY DETECTION CONFIGURATION ----------------

EXPECTED_IPS = {
    "127.0.0.1",
    "192.168.214.1",
    "192.168.214.128"
}
# Authorized systems permitted to write to Modbus registers
AUTHORIZED_WRITE_IPS = {"127.0.0.1"}


CONNECTION_WINDOW = 10
CONNECTION_THRESHOLD = 5

connection_attempts = defaultdict(deque)

ALERT_FILE = "network_alerts.csv"

alerted_unknown_sources = set()

# ---------------- CSV INITIALIZATION ----------------

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Timestamp",
            "Source IP",
            "Destination IP",
            "Source Port",
            "Destination Port",
            "Protocol",
            "TCP Flags",
            "Traffic Type"
        ])


# ---------------- SECURITY ALERT INITIALIZATION ----------------

if not os.path.exists(ALERT_FILE):
    with open(ALERT_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Timestamp",
            "Source IP",
            "Destination IP",
            "Alert Type",
            "Severity",
            "Description"
        ])


def generate_alert(source_ip, destination_ip, alert_type, severity, description):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(ALERT_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            timestamp,
            source_ip,
            destination_ip,
            alert_type,
            severity,
            description
        ])

    print(
        f"\n[SECURITY ALERT] {severity} | "
        f"{alert_type} | {description}\n"
    )

# ---------------- PACKET PROCESSING ----------------

def process_packet(packet):

    if IP not in packet or TCP not in packet:
        return

    source_ip = packet[IP].src
    destination_ip = packet[IP].dst

    source_port = packet[TCP].sport
    destination_port = packet[TCP].dport

    flags = str(packet[TCP].flags)
            # -------- MODBUS TCP VALIDATION --------

    if Raw in packet:

        payload = bytes(packet[Raw].load)

        if len(payload) >= 8:

            transaction_id = int.from_bytes(payload[0:2], "big")
            protocol_id = int.from_bytes(payload[2:4], "big")
            message_length = int.from_bytes(payload[4:6], "big")
            unit_id = payload[6]
            function_code = payload[7]

            total_length = 6 + message_length

            # Validate Modbus TCP MBAP header
            if (
                protocol_id == 0
                and message_length >= 2
                and total_length <= len(payload)
            ):

                function_names = {
                    3: "READ_HOLDING_REGISTERS",
                    6: "WRITE_SINGLE_REGISTER",
                    16: "WRITE_MULTIPLE_REGISTERS"
                }

                function_name = function_names.get(
                    function_code,
                    "UNKNOWN_FUNCTION"
                )

                print(
                    f"[MODBUS] Transaction: {transaction_id} | "
                    f"Unit: {unit_id} | "
                    f"Function Code: {function_code} | "
                    f"Operation: {function_name}"
                )

                                # -------- UNAUTHORIZED MODBUS WRITE DETECTION --------

                if (
                    packet[TCP].dport == MODBUS_PORT
                    and function_code in (6, 16)
                ):

                    if source_ip not in AUTHORIZED_WRITE_IPS:

                        generate_alert(
                            source_ip,
                            destination_ip,
                            "UNAUTHORIZED_MODBUS_WRITE",
                            "HIGH",
                            f"Write request from unauthorized IP: "
                            f"{source_ip} | Operation: {function_name}"
                        )

                    else:

                        print(
                            f"[AUTHORIZED WRITE] "
                            f"{source_ip} | {function_name}"
                        )

                    generate_alert(
                        source_ip,
                        destination_ip,
                        "MODBUS_WRITE_REQUEST",
                        "MEDIUM",
                        f"Modbus write operation detected: {function_name}"
                    )

            # -------- UNKNOWN IP DETECTION --------

    if source_ip not in EXPECTED_IPS and source_ip not in alerted_unknown_sources:

        generate_alert(
            source_ip,
            destination_ip,
            "UNKNOWN_SOURCE_IP",
            "HIGH",
            "Unexpected source IP communicating with OT network"
        )

        alerted_unknown_sources.add(source_ip)

        # -------- REPEATED CONNECTION DETECTION --------

    current_time = time.time()

    # Count only initial TCP SYN packets
    if "S" in flags and "A" not in flags:

        attempts = connection_attempts[source_ip]

        attempts.append(current_time)

        while attempts and current_time - attempts[0] > CONNECTION_WINDOW:
            attempts.popleft()

        if len(attempts) == CONNECTION_THRESHOLD + 1:

            generate_alert(
                source_ip,
                destination_ip,
                "HIGH_CONNECTION_FREQUENCY",
                "MEDIUM",
                f"{len(attempts)} TCP connection attempts "
                f"within {CONNECTION_WINDOW} seconds"
            )

# ---------------- NETWORK MONITOR ----------------

print("===================================")
print("       OT NETWORK MONITOR")
print("===================================")
print("Interface:", INTERFACE)
print("Monitoring Modbus TCP port:", MODBUS_PORT)
print("Logging to:", LOG_FILE)
print("Waiting for network traffic...")
print("Press CTRL+C to stop.\n")

try:

    sniff(
        iface=INTERFACE,
        filter=f"tcp port {MODBUS_PORT}",
        prn=process_packet,
        store=False
    )

except KeyboardInterrupt:
    print("\nNetwork monitoring stopped.")

except Exception as error:
    print("Network Monitor Error:", error)
