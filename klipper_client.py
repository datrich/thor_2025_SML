import requests


class KlipperClient:
    def __init__(self, host="http://192.168.1.18", port=7125, debug=False):
        self.host = host
        self.port = port
        self.debug = debug
        self.api_url = f"{self.host}:{self.port}"

    def test_connection(self):
        try:
            resp = requests.get(f"{self.api_url}/printer/info", timeout=3)
            return resp.status_code == 200
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Connection test failed: {e}")
            return False

    def send_gcode(self, gcode: str):
        """Send a G-code to Moonraker API properly."""
        if self.debug:
            print(f"[DEBUG] Sending G-code: {gcode}")

        url = f"{self.api_url}/printer/gcode/script"
        headers = {"Content-Type": "application/json"}
        payload = {"script": gcode}

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                if self.debug:
                    print("[DEBUG] Command sent successfully ✅")
                return True
            else:
                print(f"[ERROR] Moonraker returned {resp.status_code}: {resp.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to send command: {e}")
            return False
