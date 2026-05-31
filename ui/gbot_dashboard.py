import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

DARK  = "#0D1117"
CARD  = "#161B22"
TEAL  = "#00C9A7"
GREEN = "#3FB950"
RED   = "#F85149"
BLUE  = "#58A6FF"
GRAY  = "#8B949E"
WHITE = "#E6EDF3"

class GbotDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gbot — AI Worldbuilding Dashboard")
        self.setMinimumSize(900, 600)
        self._apply_dark_theme()
        self._build_ui()

    def _apply_dark_theme(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background: {DARK}; color: {WHITE}; }}
            QTextEdit {{ background: {CARD}; color: {WHITE}; border: 1px solid #30363D;
                        font-family: Consolas; font-size: 12px; padding: 8px; }}
            QLabel {{ color: {WHITE}; }}
            QListWidget {{ background: {CARD}; color: {WHITE};
                          border: 1px solid #30363D; font-size: 12px; }}
            QPushButton {{ background: {TEAL}; color: {DARK}; border: none;
                          padding: 8px 16px; font-weight: bold; font-size: 13px; }}
            QPushButton:hover {{ background: #00A896; }}
            QFrame {{ border: 1px solid #30363D; }}
        """)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ── Left panel: AI Reasoning log ──
        left = QVBoxLayout()
        left_label = QLabel("AI Reasoning")
        left_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        left_label.setStyleSheet(f"color: {TEAL};")
        self.ai_log = QTextEdit()
        self.ai_log.setReadOnly(True)
        self.ai_log.setPlaceholderText("AI reasoning will appear here...")
        left.addWidget(left_label)
        left.addWidget(self.ai_log)

        # ── Center panel: Workflow status ──
        center = QVBoxLayout()
        center_label = QLabel("Workflow Status")
        center_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        center_label.setStyleSheet(f"color: {BLUE};")
        self.workflow_log = QTextEdit()
        self.workflow_log.setReadOnly(True)
        self.workflow_log.setPlaceholderText("Workflow steps will appear here...")
        center.addWidget(center_label)
        center.addWidget(self.workflow_log)

        # ── Right panel: Structure list ──
        right = QVBoxLayout()
        right_label = QLabel("Structures in World")
        right_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        right_label.setStyleSheet(f"color: {GREEN};")
        self.structure_list = QListWidget()
        self.structure_count = QLabel("Total: 0")
        self.structure_count.setStyleSheet(f"color: {GRAY}; font-size: 11px;")
        right.addWidget(right_label)
        right.addWidget(self.structure_list)
        right.addWidget(self.structure_count)

        main_layout.addLayout(left, 2)
        main_layout.addLayout(center, 2)
        main_layout.addLayout(right, 1)

    def log_ai_reasoning(self, goal: str, strategy: str,
                          reasoning: str, optimization: str):
        self.ai_log.append(
            f'<span style="color:{TEAL}">━━━━━━━━━━━━━━━━━━━━━━</span><br>'
            f'<span style="color:{GRAY}">Goal:</span> '
            f'<span style="color:{WHITE}">{goal}</span><br>'
            f'<span style="color:{GRAY}">Strategy:</span> '
            f'<span style="color:{TEAL}"><b>{strategy}</b></span><br>'
            f'<span style="color:{GRAY}">Reasoning:</span> '
            f'<span style="color:{WHITE}">{reasoning}</span><br>'
            f'<span style="color:{GRAY}">Optimization:</span> '
            f'<span style="color:{WHITE}">{optimization}</span><br>'
        )

    def log_workflow(self, workflow_id: str, status: str, goal: str):
        color = GREEN if status == "complete" else RED if status == "failed" else BLUE
        self.workflow_log.append(
            f'<span style="color:{color}">■</span> '
            f'<span style="color:{GRAY}">{workflow_id}</span> '
            f'<span style="color:{WHITE}">{goal}</span> '
            f'<span style="color:{color}">[{status}]</span><br>'
        )

    def log_structure(self, name: str, type: str, location: list):
        color = {"tower": TEAL, "wall": BLUE, "outpost": GREEN}.get(type, GRAY)
        item = QListWidgetItem(f"{name}  ({type})")
        item.setForeground(QColor(color))
        self.structure_list.addItem(item)
        self.structure_count.setText(
            f"Total: {self.structure_list.count()}"
        )

    def log_step(self, step_type: str, location: list, success: bool):
        color = GREEN if success else RED
        symbol = "✓" if success else "✗"
        self.workflow_log.append(
            f'<span style="color:{color}">{symbol}</span> '
            f'<span style="color:{WHITE}">{step_type}</span> '
            f'<span style="color:{GRAY}">at {location}</span><br>'
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GbotDashboard()
    win.show()

    # Demo data to test layout
    win.log_ai_reasoning(
        "build something defendable",
        "fortress",
        "Defending the area requires a hard perimeter boundary.",
        "defense"
    )
    win.log_workflow("wf_001", "running", "build fortress")
    win.log_step("spawn_tower", [500, 500, 0], True)
    win.log_step("spawn_tower", [-500, 500, 0], True)
    win.log_step("spawn_wall", [0, 500, 0], True)
    win.log_workflow("wf_001", "complete", "build fortress")
    win.log_structure("Gbot_Tower_A1B2", "tower", [500, 500, 0])
    win.log_structure("Gbot_Tower_C3D4", "tower", [-500, 500, 0])
    win.log_structure("Gbot_Wall_E5F6", "wall", [0, 500, 0])

    sys.exit(app.exec())
