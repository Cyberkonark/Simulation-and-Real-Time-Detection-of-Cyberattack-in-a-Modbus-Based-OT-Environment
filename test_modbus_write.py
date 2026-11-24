
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient(
    "127.0.0.1",
    port=5020,
    timeout=3
)

try:
    if client.connect():
        print("Connected to Modbus Soft PLC")

        result = client.write_registers(
            address=0,
            values=[450, 285, 0],
            device_id=1
        )

        if result.isError():
            print("Write request failed:", result)
        else:
            print("Multiple-register write successful")

    else:
        print("Could not connect to Soft PLC")

finally:
    client.close()
