
import asyncio
import re
import serial

from pymodbus.simulator import SimData, SimDevice, DataType
from pymodbus.server import ModbusTcpServer

# ---------- CONFIGURATION ----------

ARDUINO_PORT = "COM3"
BAUD_RATE = 9600

MODBUS_HOST = "0.0.0.0"
MODBUS_PORT = 5020
DEVICE_ID = 1
AUTHORIZED_WRITE_IPS = {"127.0.0.1"}
SETPOINT_REGISTER = 10
# ---------- MODBUS REGISTER MODEL ----------

device = SimDevice(
    id=DEVICE_ID,
    simdata=[
        SimData(
            address=0,
            count=11,
            values=0,
            datatype=DataType.REGISTERS
        )
    ]
)

# Register mapping:
# HR0 = Water level x 10
# HR1 = LM35 temperature x 10
# HR2 = Process status (0 normal, 1 low, 2 high)

# ---------- SENSOR PROCESSING ----------

def process_sensor_data(line):

    match = re.search(
        r"Water Level:\s*([0-9.]+)%.*Temperature:\s*([0-9.]+)",
        line
    )

    if not match:
        return None

    water = float(match.group(1))
    temperature = float(match.group(2)) 

    if not (0 <= water <= 100 and 0 <= temperature <= 150):
        return None

    if water < 30:
        status = 1
    elif water > 85:
        status = 2
    else:
        status = 0

    registers = [
        round(water * 10),
        round(temperature * 10),
        status
    ]

    return water, temperature, status, registers


# ---------- MAIN SOFT PLC ----------

async def main():

    arduino = None
    server = None

    try:
        print("Connecting to Arduino...")

        arduino = serial.Serial(
            ARDUINO_PORT,
            BAUD_RATE,
            timeout=1
        )

        await asyncio.sleep(2)

        print("Arduino connected:", ARDUINO_PORT)

        server = ModbusTcpServer(
            context=device,
            address=(MODBUS_HOST, MODBUS_PORT)
        )

        await server.serve_forever(background=True)

        print("OT Soft PLC started")
        print(f"Modbus TCP: {MODBUS_HOST}:{MODBUS_PORT}")
        print("Waiting for sensor data...\n")

        while True:

            raw = await asyncio.to_thread(arduino.readline)

            line = raw.decode(
                "utf-8",
                errors="replace"
            ).strip()

            result = process_sensor_data(line)

            if result is None:
                continue

            water, temperature, status, registers = result

            await server.async_setValues(
                DEVICE_ID,
                3,
                0,
                registers
            )

            print(
                f"Water: {water:.1f}% | "
                f"Temperature: {temperature:.1f} C | "
                f"Status: {status} | "
                f"Registers: {registers}"
            )

    except KeyboardInterrupt:
        print("\nSoft PLC stopped.")

    except Exception as error:
        print("Soft PLC error:", error)

    finally:
        if arduino and arduino.is_open:
            arduino.close()

        if server:
            await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
