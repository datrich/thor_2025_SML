import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
)
from klipper_client import KlipperClient


# ---------------------- Main Control Window ---------------------- #
class ThorControlUI(QWidget):
    def __init__(self, start_positions=None):
        super().__init__()
        self.setWindowTitle("Thor Arm Control Center v6 - Manual Stepper Mode")
        self.setFixedSize(540, 580)

        layout = QVBoxLayout()

        # --- Header ---
        title = QLabel("🔧 Thor 6-DOF Manual Stepper Control")
        layout.addWidget(title)
        layout.addWidget(
            QLabel("Use + / – to move each stepper by ±10 units (absolute mode).")
        )

        # --- Backend client setup ---
        self.klipper = KlipperClient(host="http://192.168.1.96", port=7125, debug=False)

        # --- Debug and Connection Status ---
        self.debug_label = QLabel()
        self.conn_label = QLabel()
        layout.addWidget(self.debug_label)
        layout.addWidget(self.conn_label)

        # Initialize status lines
        self._update_debug_status()
        self._update_connection_status()

        # Stepper configuration
        self.steppers = {
            "J1": "stepper_j1",
            "J2": "stepper_j2",
            "J3": "stepper_j3",
            "J4": "stepper_j4",
            "J5": "stepper_j5",
            "J6": "stepper_j6",
        }

        # Initialize positions (from startup screen)
        self.positions = start_positions or {
            joint: 0.0 for joint in self.steppers.keys()
        }

        # Default move and speed
        self.default_step = 10
        self.default_speed = 5

        # --- Position Summary Line ---
        self.summary_label = QLabel(self._format_positions())
        self.summary_label.setStyleSheet(
            "font-weight: bold; padding: 6px; border: 1px solid #ccc;"
        )
        layout.addWidget(self.summary_label)

        # --- Stepper Controls ---
        self.inputs = {}
        for joint in self.steppers.keys():
            row = QHBoxLayout()
            row.addWidget(QLabel(joint))

            # Decrease button
            dec_btn = QPushButton("–")
            dec_btn.clicked.connect(lambda _, j=joint: self.move_joint(j, -1))
            row.addWidget(dec_btn)

            # Custom step input
            val_input = QLineEdit()
            val_input.setPlaceholderText("step (default 10)")
            val_input.setFixedWidth(100)
            self.inputs[joint] = val_input
            row.addWidget(val_input)

            # Increase button
            inc_btn = QPushButton("+")
            inc_btn.clicked.connect(lambda _, j=joint: self.move_joint(j, 1))
            row.addWidget(inc_btn)

            # Position display
            pos_label = QLabel(f"Pos: {self.positions[joint]}")
            pos_label.setFixedWidth(80)
            row.addWidget(pos_label)
            self.inputs[joint + "_label"] = pos_label

            layout.addLayout(row)

        # --- Status Line ---
        self.status = QLabel("Status: Ready (initialized positions applied)")
        layout.addWidget(self.status)

        # --- Manual Command Section ---
        layout.addWidget(QLabel("\nManual Command:"))
        self.command = QLineEdit()
        self.command.setPlaceholderText(
            "manual_stepper stepper=stepper_j1 move=50 speed=5"
        )
        layout.addWidget(self.command)

        send_btn = QPushButton("Send Command")
        send_btn.clicked.connect(self.send_command)
        layout.addWidget(send_btn)

        self.setLayout(layout)

    # ---------------------- Utility Functions ---------------------- #
    def _format_positions(self):
        """Create a readable text summary of all positions."""
        return "Positions → " + " | ".join(
            [f"{j}: {self.positions[j]:.2f}" for j in self.positions]
        )

    def _update_summary(self):
        """Refresh the position tracking line."""
        self.summary_label.setText(self._format_positions())

    def _update_debug_status(self):
        """Show current debug mode."""
        if self.klipper.debug:
            self.debug_label.setText("🧩 Debug Mode: ON")
            self.debug_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.debug_label.setText("🧩 Debug Mode: OFF")
            self.debug_label.setStyleSheet("color: gray;")

    def _update_connection_status(self):
        """Check connection to Moonraker API and display it."""
        ok = self.klipper.test_connection()
        if ok:
            self.conn_label.setText("🌐 Moonraker Connection: READY ✅")
            self.conn_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.conn_label.setText("🌐 Moonraker Connection: NOT CONNECTED ❌")
            self.conn_label.setStyleSheet("color: red; font-weight: bold;")

    # ---------------------- Core Actions ---------------------- #
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

        # Update UI
        self.inputs[joint + "_label"].setText(f"Pos: {pos}")
        self._update_summary()

        # Build manual_stepper command
        command = (
            f"manual_stepper stepper={stepper} move={pos} speed={self.default_speed}"
        )

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


# ---------------------- Initialization Screen ---------------------- #
class InitScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thor Arm Initialization")
        self.setFixedSize(400, 400)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("🧭 Initialize Start Position for Each Stepper"))
        layout.addWidget(
            QLabel("Enter the absolute position to begin with (default = 0).")
        )

        self.inputs = {}
        for joint in ["J1", "J2", "J3", "J4", "J5", "J6"]:
            row = QHBoxLayout()
            row.addWidget(QLabel(joint))
            inp = QLineEdit()
            inp.setPlaceholderText("0")
            row.addWidget(inp)
            layout.addLayout(row)
            self.inputs[joint] = inp

        self.confirm_btn = QPushButton("Confirm and Start")
        self.confirm_btn.clicked.connect(self.confirm)
        layout.addWidget(self.confirm_btn)

        self.status = QLabel("")
        layout.addWidget(self.status)

        self.setLayout(layout)
        self.positions = None  # store user positions

    def confirm(self):
        """Collect initial positions and launch main window."""
        positions = {}
        try:
            for joint, field in self.inputs.items():
                txt = field.text().strip()
                positions[joint] = float(txt) if txt else 0.0
            self.positions = positions
            self.close()
        except ValueError:
            self.status.setText("❌ Invalid value — please enter numeric positions.")


# ---------------------- Main Entry Point ---------------------- #
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Step 1: Show initialization window
    init_window = InitScreen()
    init_window.show()
    app.exec()

    # Step 2: When closed, if positions were entered, open control UI
    if init_window.positions is not None:
        main_window = ThorControlUI(start_positions=init_window.positions)
        main_window.show()
        sys.exit(app.exec())
