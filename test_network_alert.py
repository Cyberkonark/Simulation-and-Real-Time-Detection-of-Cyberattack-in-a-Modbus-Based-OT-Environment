
import socket
import time

HOST = "127.0.0.1"
PORT = 5020

print("Starting controlled connection test...")

for attempt in range(6):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        connection.connect((HOST, PORT))
        print(f"Test connection {attempt + 1}: Successful")

    except OSError as error:
        print(f"Test connection {attempt + 1}: Failed - {error}")

    finally:
        connection.close()

    time.sleep(0.2)

print("Test completed.")
