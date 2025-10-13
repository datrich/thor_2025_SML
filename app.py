import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout
)
from klipper_client import KlipperClient


class ThorControlUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thor Arm Control Center v1")
        self.setFixedSize(400, 250)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Manual Command:"))

        self.command = QLineEdit()
        self.command.setPlaceholderText("Enter G-code (e.g. G0 X10 Y20 Z5 F3000)")
        layout.addWidget(self.command)

        send_btn = QPushButton("Send Command")
        send_btn.clicked.connect(self.send_command)
        layout.addWidget(send_btn)

        # Preset buttons
        layout.addWidget(QLabel("Quick Actions:"))
        btn_row = QHBoxLayout()
        presets = {
            "Home": "G28",
            "Move +X": "G91\nG0 X10 F3000\nG90",
            "Move -X": "G91\nG0 X-10 F3000\nG90",
        }
        for label, cmd in presets.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, c=cmd: self.send_preset(c))
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

        self.status = QLabel("Status: Ready")
        layout.addWidget(self.status)

        self.setLayout(layout)

        # Backend
        self.klipper = KlipperClient("http://localhost:7125")

    def send_command(self):
        gcode = self.command.text().strip()
        if not gcode:
            self.status.setText("Status: No command entered.")
            return
        self.status.setText(f"Status: Sending '{gcode}'...")
        response = self.klipper.send_gcode(gcode)
        if response:
            self.status.setText("Status: Command sent ✅")
        else:
            self.status.setText("Status: Failed ❌")

    def send_preset(self, gcode):
        self.status.setText(f"Status: Sending preset '{gcode}'...")
        response = self.klipper.send_gcode(gcode)
        if response:
            self.status.setText("Status: Preset sent ✅")
        else:
            self.status.setText("Status: Failed ❌")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThorControlUI()
    window.show()
    sys.exit(app.exec())
