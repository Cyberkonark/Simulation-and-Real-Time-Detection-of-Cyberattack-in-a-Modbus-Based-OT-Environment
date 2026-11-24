
from pymodbus.client import ModbusTcpClient
import time

HOST = "127.0.0.1"
PORT = 5020
DEVICE_ID = 1

client = ModbusTcpClient(HOST, port=PORT, timeout=3)

try:
    print("Connecting to Modbus TCP server...")

    if not client.connect():
        print("Connection failed!")
        raise SystemExit

    print("Modbus TCP connection successful!\n")

    while True:
        result = client.read_holding_registers(
            address=0,
            count=3,
            device_id=DEVICE_ID
        )

        if result.isError():
            print("Register read error:", result)
        else:
            registers = result.registers

            water_level = registers[0] / 10
            temperature = registers[1] / 10
            status = registers[2]

            print(
                f"Water Level: {water_level:.1f}% | "
                f"Temperature: {temperature:.1f} C | "
                f"Process Status: {status} | "
                f"Raw Registers: {registers}"
            )

        time.sleep(2)

except KeyboardInterrupt:
    print("\nModbus client stopped.")

except Exception as error:
    print("Client error:", error)

finally:
    client.close()
    print("Modbus connection closed.")
