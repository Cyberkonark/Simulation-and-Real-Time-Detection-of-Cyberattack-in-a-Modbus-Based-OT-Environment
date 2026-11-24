
alerted_unknown_sources = set()
expected_ips = {"127.0.0.1"}

def check_unknown_ip(source_ip, destination_ip):
    if source_ip not in expected_ips and source_ip not in alerted_unknown_sources:
        print(
            f"[SECURITY ALERT] HIGH | UNKNOWN_SOURCE_IP | "
            f"{source_ip} -> {destination_ip}"
        )
        alerted_unknown_sources.add(source_ip)

# Simulate three packets from the same unexpected source
for attempt in range(3):
    check_unknown_ip("192.0.2.10", "127.0.0.1")

