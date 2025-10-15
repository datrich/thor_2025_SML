import requests
import json

class KlipperClient:
    def __init__(self, host="http://192.168.1.96", port=7125, debug=True):
        """
        host: IP or hostname of Moonraker (without trailing slash)
        port: Moonraker API port
        debug: if True, print outgoing commands instead of sending
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.base_url = f"{self.host}:{self.port}"

    # ------------------- Internal Utilities ------------------- #
    def _get_url(self, path):
        """Build full URL for Moonraker API."""
        return f"{self.base_url}{path}"

    def _print_debug(self, message):
        """Helper to print clearly formatted debug output."""
        print(f"[DEBUG] {message}")

    # ------------------- Public Interface ------------------- #
    def send_gcode(self, cmd):
        """
        Send a G-code command through Moonraker API.
        Example: manual_stepper stepper=stepper_j1 move=50 speed=5
        """
        if self.debug:
            self._print_debug(f"Would send → {cmd}")
            return {"debug": True, "command": cmd}

        try:
            url = self._get_url("/printer/gcode/script")
            payload = {"script": cmd}
            r = requests.post(url, json=payload, timeout=3)
            if r.status_code == 200:
                return r.json()
            else:
                print(f"[ERROR] Moonraker returned {r.status_code}: {r.text}")
                return None
        except Exception as e:
            print(f"[ERROR] Failed to send command: {e}")
            return None

    def query_toolhead(self):
        """
        Query toolhead info (example endpoint).
        Returns position, status, etc.
        """
        try:
            url = self._get_url("/printer/objects/query?toolhead")
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                return r.json()
            else:
                print(f"[ERROR] Query failed ({r.status_code}): {r.text}")
                return None
        except Exception as e:
            print(f"[ERROR] Query exception: {e}")
            return None

    def test_connection(self):
        """
        Check connection to Moonraker (returns True/False).
        """
        try:
            url = self._get_url("/printer/info")
            r = requests.get(url, timeout=3)
            return r.status_code == 200
        except Exception:
            return False


# ------------------- Standalone Test ------------------- #
if __name__ == "__main__":
    kc = KlipperClient(debug=False)
    print("🔌 Testing Klipper Client Connection...")
    ok = kc.test_connection()
    print(f"Moonraker Connection: {'READY ✅' if ok else 'FAILED ❌'}")

    if ok:
        print("\nSending M115 (printer info)...")
        res = kc.send_gcode("M115")
        print(json.dumps(res, indent=4))

        print("\nQuerying toolhead...")
        res = kc.query_toolhead()
        print(json.dumps(res, indent=4))
