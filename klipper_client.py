import requests

class KlipperClient:
    def __init__(self, host="http://localhost:7125"):
        self.host = host.rstrip("/")

    def send_gcode(self, command: str):
        """Send a G-code command via Moonraker."""
        url = f"{self.host}/printer/gcode/script"
        try:
            r = requests.post(url, json={"script": command})
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"[Error] Failed to send G-code: {e}")
            return None
