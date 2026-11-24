
import socket
import socketserver
import struct
import csv
from datetime import datetime

LISTEN_IP = "192.168.214.1"
LISTEN_PORT = 15020

PLC_IP = "127.0.0.1"
PLC_PORT = 5020

TEST_REGISTER = 10
INJECTED_VALUE = 500

LOG_FILE = "network_alerts.csv"


def receive_exact(sock, size):
    data = b""

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            raise ConnectionError("Connection closed")

        data += chunk

    return data


def log_mitm_event(source_ip, original, injected):

    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            event_time,
            source_ip,
            PLC_IP,
            "MODBUS_SETPOINT_INJECTION",
            "CRITICAL",
            f"HR{TEST_REGISTER} injection attempt: "
            f"original={original}, injected={injected}, action=BLOCKED"
        ])

    print("[SECURITY ALERT] CRITICAL | MODBUS_SETPOINT_INJECTION")
    print(f"[SECURITY ALERT] Original value: {original}")
    print(f"[SECURITY ALERT] Attempted injected value: {injected}")
    print("[PREVENTION] Injection attempt logged and blocked")


class ModbusMITMHandler(socketserver.BaseRequestHandler):

    def handle(self):

        print(f"\n[MITM] Client connected: {self.client_address[0]}")

        try:
            with socket.create_connection(
                (PLC_IP, PLC_PORT), timeout=5
            ) as plc:

                while True:

                    header = receive_exact(self.request, 7)

                    length = struct.unpack(">H", header[4:6])[0]

                    if length < 2 or length > 254:
                        raise ValueError("Invalid Modbus frame length")

                    body = receive_exact(self.request, length - 1)

                    request = bytearray(header + body)

                    if len(request) >= 12:

                        function = request[7]
                        register = struct.unpack(">H", request[8:10])[0]

                        if function == 6 and register == TEST_REGISTER:

                            original = struct.unpack(
                                ">H", request[10:12]
                            )[0]

                            if original == INJECTED_VALUE:

                                print(
                                    "[PREVENTION] Unauthorized "
                                    "injected value detected"
                                )

                                log_mitm_event(
                                    self.client_address[0],
                                    "NOT_FORWARDED",
                                    original
                                )

                                # Reject the injected request.
                                # Do not forward it to the PLC.
                                exception_response = (
                                    header[:4]
                                    + struct.pack(">H", 3)
                                    + bytes([header[6], function | 0x80, 0x03])
                                )

                                self.request.sendall(exception_response)
                                continue

                            print("[MITM] Test register write observed")
                            print(f"[MITM] HR10 requested value: {original}")

                    plc.sendall(request)

                    response_header = receive_exact(plc, 7)

                    response_length = struct.unpack(
                        ">H", response_header[4:6]
                    )[0]

                    response_body = receive_exact(
                        plc, response_length - 1
                    )

                    self.request.sendall(
                        response_header + response_body
                    )

        except (ConnectionError, OSError, ValueError) as error:
            print(f"[MITM] Connection ended: {error}")


class MITMServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":

    print("========== MODBUS MITM PROXY ==========")
    print(f"Listening: {LISTEN_IP}:{LISTEN_PORT}")
    print(f"PLC target: {PLC_IP}:{PLC_PORT}")
    print(f"Protected test register: HR{TEST_REGISTER}")
    print("Injection detection enabled")
    print("Injection prevention enabled")
    print("Automatic security logging enabled")
    print("=======================================")

    with MITMServer(
        (LISTEN_IP, LISTEN_PORT),
        ModbusMITMHandler
    ) as server:

        server.serve_forever()
