# test_klipper_connection.py

from klipper_client import KlipperClient
import json

if __name__ == "__main__":
    # ⚙️ Replace with your Moonraker host and port
    host = "http://192.168.1.18"
    port = 7125

    print(f"🔌 Testing connection to Moonraker at {host}:{port} ...")
    client = KlipperClient(host=host, port=port, debug=False)

    # 1️⃣ Basic connection test
    ok = client.test_connection()
    print(f"✅ Connection Status: {'READY' if ok else 'FAILED'}")

    if not ok:
        print("❌ Could not reach Moonraker. Check IP, port, or Klipper service.")
    else:
        # 2️⃣ Test sending a G-code command
        print("\n📡 Sending test G-code: M115 (printer info)")
        res = client.send_gcode("M115")
        print(json.dumps(res, indent=4))

        # 3️⃣ Try a structured query
        print("\n📊 Querying toolhead data:")
        qres = client.query_toolhead()
        print(json.dumps(qres, indent=4))
