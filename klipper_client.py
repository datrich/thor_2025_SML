import requests

class KlipperClient:
    def __init__(self, host="http://localhost:7125", debug=True):
        """
        :param host: URL of the Moonraker API server
        :param debug: If True, print data instead of sending it
        """
        self.host = host.rstrip("/")
        self.debug = debug

    # ---------------------------------------------------
    # MAIN METHOD: called by your UI
    # ---------------------------------------------------
    def send_gcode(self, command: str):
        """
        Send (or simulate sending) a G-code command to Klipper via Moonraker API.
        In debug mode, it prints the payload instead of making the HTTP request.
        """
        url = f"{self.host}/printer/gcode/script"
        payload = {"script": command}

        if self.debug:
            print("\n[DEBUG] ---- Sending G-code to Moonraker ----")
            print(f"POST {url}")
            print(f"Payload: {payload}")
            print("[DEBUG] --------------------------------------\n")
            return {"debug": True, "sent_command": command}

        # Actual send mode (disabled by default)
        try:
            r = requests.post(url, json=payload)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"[Error] Failed to send G-code: {e}")
            return None

    # ---------------------------------------------------
    # OPTIONAL: A method to query printer state
    # ---------------------------------------------------
    def get_status(self):
        """
        Example of how you'd query Moonraker for printer status.
        Not used yet, but useful for future features.
        """
        url = f"{self.host}/printer/info"
        if self.debug:
            print(f"[DEBUG] Would GET {url}")
            return {"debug": True, "status": "mocked"}
        try:
            r = requests.get(url)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"[Error] Failed to get printer status: {e}")
            return None
