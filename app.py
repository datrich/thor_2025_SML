import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel
)
from klipper_client import KlipperClient


class ThorControlUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thor Arm Control Center v3 - Manual Stepper Mode")
        self.setFixedSize(480, 500)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("🔧 Thor 6-DOF Manual Stepper Control"))
        layout.addWidget(QLabel("Use + / – to move each stepper by ±10 units (absolute mode)."))

        # Backend client
        self.klipper = KlipperClient("http://localhost:7125", debug=True)

        # Stepper names must match your Klipper config
        # Example: stepper_j1, stepper_j2, ...
        self.steppers = {
            "J1": "stepper_j1",
            "J2": "stepper_j2",
            "J3": "stepper_j3",
            "J4": "stepper_j4",
            "J5": "stepper_j5",
            "J6": "stepper_j6",
        }

        # Internal absolute positions (all start at 0)
        self.positions = {joint: 0.0 for joint in self.steppers.keys()}

        # Default move and speed
        self.default_step = 10
        self.default_speed = 5  # speed units as per your setup

        # Build the UI
        self.inputs = {}
        for joint in self.steppers.keys():
            row = QHBoxLayout()
            row.addWidget(QLabel(joint))

            # Decrease
            dec_btn = QPushButton("–")
            dec_btn.clicked.connect(lambda _, j=joint: self.move_joint(j, -1))
            row.addWidget(dec_btn)

            # Custom step input
            val_input = QLineEdit()
            val_input.setPlaceholderText("step (default 10)")
            val_input.setFixedWidth(100)
            self.inputs[joint] = val_input
            row.addWidget(val_input)

            # Increase
            inc_btn = QPushButton("+")
            inc_btn.clicked.connect(lambda _, j=joint: self.move_joint(j, 1))
            row.addWidget(inc_btn)

            # Display current position
            pos_label = QLabel(f"Pos: 0")
            pos_label.setFixedWidth(80)
            row.addWidget(pos_label)
            self.inputs[joint + "_label"] = pos_label

            layout.addLayout(row)

        # Status
        self.status = QLabel("Status: Ready (all positions set to 0)")
        layout.addWidget(self.status)

        # Manual command section
        layout.addWidget(QLabel("\nManual Command:"))
        self.command = QLineEdit()
        self.command.setPlaceholderText("manual_stepper stepper=stepper_j1 move=50 speed=5")
        layout.addWidget(self.command)

        send_btn = QPushButton("Send Command")
        send_btn.clicked.connect(self.send_command)
        layout.addWidget(send_btn)

        self.setLayout(layout)

    # ---------------- Core Actions ---------------- #
    def move_joint(self, joint, direction):
        """Increase or decrease absolute position and send manual_stepper command."""
        try:
            val_text = self.inputs[joint].text().strip()
            step = float(val_text) if val_text else self.default_step
        except ValueError:
            self.status.setText(f"Status: Invalid step value for {joint}")
            return

        # Update internal absolute position
        self.positions[joint] += direction * step
        pos = self.positions[joint]
        stepper = self.steppers[joint]

        # Update label
        self.inputs[joint + "_label"].setText(f"Pos: {pos}")

        # Build manual_stepper command
        command = f"manual_stepper stepper={stepper} move={pos} speed={self.default_speed}"

        # Send (or print in debug)
        response = self.klipper.send_gcode(command)
        if response:
            self.status.setText(f"Status: {joint} moved to {pos} ✅")
        else:
            self.status.setText(f"Status: Failed to move {joint} ❌")

    def send_command(self):
        """Send a custom manual_stepper command manually."""
        cmd = self.command.text().strip()
        if not cmd:
            self.status.setText("Status: No command entered.")
            return
        self.status.setText(f"Status: Sending custom command...")
        response = self.klipper.send_gcode(cmd)
        if response:
            self.status.setText(f"Status: Custom command sent ✅")
        else:
            self.status.setText(f"Status: Failed ❌")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThorControlUI()
    window.show()
    sys.exit(app.exec())
