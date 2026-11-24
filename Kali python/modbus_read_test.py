from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient(
    host="192.168.214.1",
    port=5020,
    timeout=3
)

if client.connect():
    result = client.read_holding_registers(
        address=10,
        count=1,
        device_id=1
    )

    if not result.isError():
        print("[+] Test register HR10 accessible")
        print("HR10 value:", result.registers[0])
    else:
        print("[-] Read failed:", result)

    client.close()
else:
    print("[-] Connection failed")
