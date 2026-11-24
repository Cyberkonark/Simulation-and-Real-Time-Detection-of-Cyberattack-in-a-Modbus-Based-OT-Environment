from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient(
    host="192.168.214.1",
    port=5020,
    timeout=3
)

if client.connect():
    print("[+] Connected to OT Soft PLC")

    result = client.write_register(
        address=10,
        value=500,
        device_id=1
    )

    if not result.isError():
        print("[+] Test setpoint written to HR10")

        verify = client.read_holding_registers(
            address=10,
            count=1,
            device_id=1
        )

        if not verify.isError():
            print("Verified HR10 value:", verify.registers[0])
    else:
        print("[-] Write failed:", result)

    client.close()
else:
    print("[-] Connection failed")
