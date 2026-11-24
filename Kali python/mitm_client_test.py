
import socket
import struct

HOST = "192.168.214.1"
PORT = 15020


def receive_exact(sock, size):
    data = b""

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            raise ConnectionError("Connection closed")

        data += chunk

    return data


def transact(sock, transaction, pdu):

    request = (
        struct.pack(">HHHB", transaction, 0, len(pdu) + 1, 1)
        + pdu
    )

    sock.sendall(request)

    header = receive_exact(sock, 7)

    length = struct.unpack(">H", header[4:6])[0]

    return header + receive_exact(sock, length - 1)


def main():

    try:
        with socket.create_connection(
            (HOST, PORT), timeout=5
        ) as sock:

            print("[CLIENT] Connected through MITM proxy")

            # Send test value 100 to HR10
            response = transact(
                sock,
                1,
                struct.pack(">BHH", 6, 10, 500)
            )

            print("[CLIENT] Requested HR10 = 500")
            print("[CLIENT] Write response:", response.hex())

            # Read HR10 back from PLC
            response = transact(
                sock,
                2,
                struct.pack(">BHH", 3, 10, 1)
            )

            value = struct.unpack(">H", response[-2:])[0]

            print("[CLIENT] Value read back from PLC:", value)

            if value == 500:
                print("[RESULT] MITM injection verified")
            elif value == 100:
                print("[RESULT] Original value preserved")
            else:
                print("[RESULT] Unexpected register value:", value)

    except Exception as error:
        print("[CLIENT] Test failed:", error)


if __name__ == "__main__":
    main()
