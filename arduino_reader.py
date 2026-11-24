
import serial
import time

# Change COM4 to your Arduino's actual port
ARDUINO_PORT = "COM3"
BAUD_RATE = 9600

try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2)

    print("Connected to Arduino Uno!")
    print("Waiting for sensor readings...\n")

    time.sleep(2)

    while True:
        if arduino.in_waiting > 0:
            data = arduino.readline().decode(
                "utf-8", errors="replace"
            ).strip()

            if data:
                print("Arduino Sensor Data:", data)

except serial.SerialException as error:
    print("Serial connection error:", error)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")

finally:
    if "arduino" in locals() and arduino.is_open:
        arduino.close()
        print("Arduino connection closed.")
