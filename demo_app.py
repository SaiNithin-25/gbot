"""
gbot/demo_app.py
Standalone Gbot UI — run from VS Code or terminal.
Communicates with UE via socket.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFrame, QFileDialog, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor
import gbot_client

# ── Colors ────────────────────────────────────────────
DARK   = "#0D1117"
CARD   = "#161B22"
BORDER = "#30363D"
TEAL   = "#00C9A7"
GREEN  = "#3FB950"
RED    = "#F85149"
BLUE   = "#58A6FF"
AMBER  = "#E3B341"
GRAY   = "#8B949E"
WHITE  = "#E6EDF3"


class SignalBridge(QObject):
    result_ready = pyqtSignal(dict, str)


class GbotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gbot — AI Worldbuilding Assistant")
        self.setMinimumSize(860, 620)
        self._bridge = SignalBridge()
        self._bridge.result_ready.connect(self._on_result)
        self._project_path = ""
        self._apply_theme()
        self._build_ui()

        # Connection polling
        self._conn_timer = QTimer()
        self._conn_timer.timeout.connect(self._check_connection)
        self._conn_timer.start(3000)
        self._check_connection()

    def _apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: {DARK}; color: {WHITE};
                font-family: 'Segoe UI', Arial; font-size: 13px;
            }}
            QTextEdit {{
                background: {CARD}; color: {WHITE};
                border: 1px solid {BORDER};
                font-family: Consolas; font-size: 12px;
                padding: 10px; border-radius: 6px;
            }}
            QLineEdit {{
                background: {CARD}; color: {WHITE};
                border: 1px solid {BORDER};
                padding: 10px 14px; border-radius: 6px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border: 1px solid {TEAL}; }}
            QPushButton {{
                background: {TEAL}; color: {DARK};
                border: none; padding: 10px 20px;
                font-weight: bold; font-size: 13px;
                border-radius: 6px;
            }}
            QPushButton:hover {{ background: #00A896; }}
            QPushButton:disabled {{ background: {BORDER}; color: {GRAY}; }}
            QLabel {{ color: {WHITE}; }}
        """)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ── Header ──
        header = QHBoxLayout()

        # Logo + title
        title = QLabel("Gbot")
        title.setFont(QFont("Arial Black", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEAL};")
        subtitle = QLabel("AI Procedural Worldbuilding for Unreal Engine 5")
        subtitle.setStyleSheet(f"color: {GRAY}; font-size: 11px;")
        title_col = QVBoxLayout()
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        title_col.setSpacing(0)

        # Connection indicator
        self._conn_dot = QLabel("●")
        self._conn_dot.setFont(QFont("Arial", 18))
        self._conn_dot.setStyleSheet(f"color: {RED};")
        self._conn_label = QLabel("UE Not Connected")
        self._conn_label.setStyleSheet(f"color: {RED}; font-size: 11px;")
        conn_col = QVBoxLayout()
        conn_col.addWidget(self._conn_dot, alignment=Qt.AlignmentFlag.AlignCenter)
        conn_col.addWidget(self._conn_label, alignment=Qt.AlignmentFlag.AlignCenter)
        conn_col.setSpacing(0)

        header.addLayout(title_col)
        header.addStretch()
        header.addLayout(conn_col)
        root.addLayout(header)

        # ── Divider ──
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {BORDER};")
        root.addWidget(line)

        # ── Project path ──
        proj_row = QHBoxLayout()
        proj_label = QLabel("UE Project:")
        proj_label.setStyleSheet(f"color: {GRAY}; font-size: 11px;")
        proj_label.setFixedWidth(80)
        self._proj_input = QLineEdit()
        self._proj_input.setPlaceholderText("D:/Game ideas/Gbot_test/  (optional)")
        self._proj_input.setStyleSheet(
            f"background: {CARD}; color: {GRAY}; border: 1px solid {BORDER};"
            f"padding: 6px 12px; border-radius: 6px; font-size: 11px;"
        )
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(80)
        browse_btn.setStyleSheet(
            f"background: {CARD}; color: {TEAL}; border: 1px solid {TEAL};"
            f"padding: 6px 12px; border-radius: 6px; font-size: 11px;"
            f"font-weight: bold;"
        )
        browse_btn.clicked.connect(self._browse_project)
        proj_row.addWidget(proj_label)
        proj_row.addWidget(self._proj_input)
        proj_row.addWidget(browse_btn)
        root.addLayout(proj_row)

        # ── Output log ──
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMinimumHeight(340)
        self._log_append(
            f'<span style="color:{TEAL}">Gbot ready.</span> '
            f'<span style="color:{GRAY}">Start gbot_server.py in UE, then send commands.</span>'
        )
        self._log_append(
            f'<span style="color:{GRAY}">Try: </span>'
            f'<span style="color:{WHITE}">build fortress</span>'
            f'<span style="color:{GRAY}"> · </span>'
            f'<span style="color:{WHITE}">build something defendable</span>'
            f'<span style="color:{GRAY}"> · </span>'
            f'<span style="color:{AMBER}">grill_the_world</span>'
        )
        root.addWidget(self._log)

        # ── Command input ──
        cmd_row = QHBoxLayout()
        self._cmd_input = QLineEdit()
        self._cmd_input.setPlaceholderText(
            "Type a command... (build fortress · build something defendable · grill_the_world)"
        )
        self._cmd_input.returnPressed.connect(self._send_command)
        self._send_btn = QPushButton("Send")
        self._send_btn.setFixedWidth(90)
        self._send_btn.clicked.connect(self._send_command)
        grill_btn = QPushButton("⚡ Grill the World")
        grill_btn.setFixedWidth(150)
        grill_btn.setStyleSheet(
            f"background: {AMBER}; color: {DARK}; border: none;"
            f"padding: 10px 20px; font-weight: bold; font-size: 13px;"
            f"border-radius: 6px;"
        )
        grill_btn.clicked.connect(self._grill_world)
        cmd_row.addWidget(self._cmd_input)
        cmd_row.addWidget(self._send_btn)
        cmd_row.addWidget(grill_btn)
        root.addLayout(cmd_row)

    def _log_append(self, html: str):
        self._log.append(html)
        self._log.moveCursor(QTextCursor.MoveOperation.End)

    def _check_connection(self):
        def check():
            connected = gbot_client.ping()
            # Update UI on main thread via timer
            self._pending_conn = connected
            QTimer.singleShot(0, self._update_conn_ui)
        import threading
        threading.Thread(target=check, daemon=True).start()

    def _update_conn_ui(self):
        connected = getattr(self, "_pending_conn", False)
        if connected:
            self._conn_dot.setStyleSheet(f"color: {GREEN};")
            self._conn_label.setText("UE Connected")
            self._conn_label.setStyleSheet(f"color: {GREEN}; font-size: 11px;")
            self._send_btn.setEnabled(True)
        else:
            self._conn_dot.setStyleSheet(f"color: {RED};")
            self._conn_label.setText("UE Not Connected")
            self._conn_label.setStyleSheet(f"color: {RED}; font-size: 11px;")

    def _browse_project(self):
        path = QFileDialog.getExistingDirectory(self, "Select UE Project Folder")
        if path:
            self._project_path = path
            self._proj_input.setText(path)
            self._log_append(
                f'<span style="color:{GRAY}">Project path set: </span>'
                f'<span style="color:{TEAL}">{path}</span>'
            )

    def _send_command(self):
        command = self._cmd_input.text().strip()
        if not command:
            return
        if command.lower() == "grill_the_world":
            self._grill_world()
            self._cmd_input.clear()
            return
        self._cmd_input.clear()
        self._send_btn.setEnabled(False)
        self._log_append(
            f'<br><span style="color:{TEAL}">▶ Gbot&gt;</span> '
            f'<span style="color:{WHITE}">{command}</span>'
        )
        gbot_client.send_async(command, lambda r: self._bridge.result_ready.emit(r, command))

    def _grill_world(self):
        self._send_btn.setEnabled(False)
        self._log_append(
            f'<br><span style="color:{AMBER}">⚡ grill_the_world</span> '
            f'<span style="color:{GRAY}">— scanning world and asking AI...</span>'
        )
        gbot_client.send_async("grill_the_world", lambda r: self._bridge.result_ready.emit(r, "grill_the_world"))

    def _on_result(self, result: dict, command: str):
        self._send_btn.setEnabled(True)
        status = result.get("status", "error")

        if command == "grill_the_world":
            if status == "ok":
                data = result
                self._log_append(
                    f'<br><span style="color:{AMBER}">━━━ World Report ━━━</span><br>'
                    f'<span style="color:{GRAY}">Total actors:</span> '
                    f'<span style="color:{WHITE}">{data.get("total_actors", "?")}</span><br>'
                    f'<span style="color:{GRAY}">Gbot structures:</span> '
                    f'<span style="color:{TEAL}">{data.get("gbot_structures", "?")}</span><br>'
                    f'<span style="color:{GRAY}">Types:</span> '
                    f'<span style="color:{WHITE}">{data.get("structure_types", {})}</span><br><br>'
                    f'<span style="color:{AMBER}">AI Summary:</span><br>'
                    f'<span style="color:{WHITE}">{data.get("summary", "No summary.")}</span><br>'
                    f'<span style="color:{AMBER}">━━━━━━━━━━━━━━━━━━━</span>'
                )
            else:
                self._log_append(
                    f'<span style="color:{RED}">✗ Error: {result.get("message", "unknown")}</span>'
                )
        else:
            if status == "ok":
                report = result.get("report", {})
                count = report.get("structure_count", "?")
                wf_id = report.get("workflow_id", "?")
                self._log_append(
                    f'<span style="color:{GREEN}">✓ Complete</span> '
                    f'<span style="color:{GRAY}">· {wf_id} · {count} structures in world</span>'
                )
            else:
                self._log_append(
                    f'<span style="color:{RED}">✗ {result.get("message", "unknown error")}</span>'
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GbotApp()
    win.show()
    sys.exit(app.exec())
