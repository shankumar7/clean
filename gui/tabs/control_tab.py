"""
Tab 2: System Controls, Relay Motor Override & Safety Threshold Settings (With Theme Support).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QSpinBox, QScrollArea
)
from PyQt6.QtCore import Qt
from gui.theme import ThemeManager


class ControlTab(QWidget):
    def __init__(self, monitor_engine, parent=None):
        super().__init__(parent)
        self.monitor = monitor_engine
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(6, 6, 6, 6)
        content_layout.setSpacing(10)
        
        # Title
        self.title_lbl = QLabel("SYSTEM CONTROL & SAFETY THRESHOLDS")
        content_layout.addWidget(self.title_lbl)
        
        # Notice Box
        self.notice_box = QFrame()
        notice_layout = QVBoxLayout(self.notice_box)
        notice_layout.setContentsMargins(12, 8, 12, 8)
        notice_layout.setSpacing(2)
        
        self.notice_title = QLabel("AUTOMATED SAFETY ENGINE ACTIVE")
        self.notice_body = QLabel("The system automatically runs the motor relay when PM2.5 goes over threshold limit.")
        self.notice_body.setWordWrap(True)
        
        notice_layout.addWidget(self.notice_title)
        notice_layout.addWidget(self.notice_body)
        content_layout.addWidget(self.notice_box)
        
        # Section 1: System Mode Selector
        self.mode_frame = QFrame()
        mode_layout = QHBoxLayout(self.mode_frame)
        mode_layout.setContentsMargins(12, 10, 12, 10)
        
        mode_info = QVBoxLayout()
        self.mode_lbl = QLabel("System Mode Override")
        self.mode_sub = QLabel("Switch between auto safety control & manual user override.")
        mode_info.addWidget(self.mode_lbl)
        mode_info.addWidget(self.mode_sub)
        
        mode_layout.addLayout(mode_info, stretch=1)
        
        self.mode_btn = QPushButton("AUTO MODE")
        self.mode_btn.setMinimumHeight(36)
        self.mode_btn.setMinimumWidth(130)
        self.mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_btn.clicked.connect(self._toggle_mode)
        mode_layout.addWidget(self.mode_btn)
        
        content_layout.addWidget(self.mode_frame)
        
        # Section 2: Relay Motor Control
        self.motor_frame = QFrame()
        motor_layout = QHBoxLayout(self.motor_frame)
        motor_layout.setContentsMargins(12, 10, 12, 10)
        
        motor_info = QVBoxLayout()
        self.motor_lbl = QLabel("Manual Motor Relay")
        self.motor_sub = QLabel("Trigger GPIO 23 relay output directly.")
        motor_info.addWidget(self.motor_lbl)
        motor_info.addWidget(self.motor_sub)
        
        motor_layout.addLayout(motor_info, stretch=1)
        
        self.motor_btn = QPushButton("MOTOR OFF")
        self.motor_btn.setMinimumHeight(36)
        self.motor_btn.setMinimumWidth(130)
        self.motor_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.motor_btn.clicked.connect(self._toggle_motor)
        motor_layout.addWidget(self.motor_btn)
        
        content_layout.addWidget(self.motor_frame)
        
        # Section 3: Threshold Limit Adjuster
        self.thresh_frame = QFrame()
        thresh_layout = QHBoxLayout(self.thresh_frame)
        thresh_layout.setContentsMargins(12, 10, 12, 10)
        
        thresh_info = QVBoxLayout()
        self.thresh_lbl = QLabel("PM2.5 Safety Trigger Limit")
        self.thresh_sub = QLabel("Concentration level that triggers motor relay.")
        thresh_info.addWidget(self.thresh_lbl)
        thresh_info.addWidget(self.thresh_sub)
        
        thresh_layout.addLayout(thresh_info, stretch=1)
        
        self.spinbox = QSpinBox()
        self.spinbox.setRange(20, 500)
        self.spinbox.setSingleStep(10)
        self.spinbox.setValue(200)
        self.spinbox.setSuffix(" µg/m³")
        self.spinbox.setMinimumHeight(34)
        self.spinbox.setMinimumWidth(120)
        self.spinbox.valueChanged.connect(self._threshold_changed)
        thresh_layout.addWidget(self.spinbox)
        
        content_layout.addWidget(self.thresh_frame)
        content_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        self.apply_theme(ThemeManager.get_theme())

    def apply_theme(self, theme):
        self.title_lbl.setStyleSheet(f"color: {theme['accent']}; font-size: 12px; font-weight: bold; letter-spacing: 0.5px;")
        
        frame_style = f"""
            QFrame {{
                background-color: {theme['card_bg']};
                border: 1px solid {theme['card_border']};
                border-radius: 12px;
            }}
        """
        self.mode_frame.setStyleSheet(frame_style)
        self.motor_frame.setStyleSheet(frame_style)
        self.thresh_frame.setStyleSheet(frame_style)
        
        self.mode_lbl.setStyleSheet(f"color: {theme['text_primary']}; font-size: 13px; font-weight: bold;")
        self.mode_sub.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 10px;")
        
        self.motor_lbl.setStyleSheet(f"color: {theme['text_primary']}; font-size: 13px; font-weight: bold;")
        self.motor_sub.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 10px;")
        
        self.thresh_lbl.setStyleSheet(f"color: {theme['text_primary']}; font-size: 13px; font-weight: bold;")
        self.thresh_sub.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 10px;")
        
        self.spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: {theme['bg']};
                color: {theme['text_primary']};
                border: 2px solid {theme['accent']};
                border-radius: 8px;
                padding: 2px 6px;
                font-size: 13px;
                font-weight: bold;
            }}
        """)

    def _toggle_mode(self):
        current_mode = self.monitor.manual_mode
        self.monitor.set_manual_mode(not current_mode)

    def _toggle_motor(self):
        current_motor = self.monitor.motor_state
        self.monitor.set_motor_state(not current_motor)

    def _threshold_changed(self, val):
        self.monitor.set_pm25_threshold(val)

    def update_ui(self, state):
        manual = (state["manual"] == 1)
        motor = (state["motor"] == 1)
        thresh = state.get("pm25_threshold", 200)
        
        if self.spinbox.value() != thresh:
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(thresh)
            self.spinbox.blockSignals(False)

        if manual:
            self.mode_btn.setText("MANUAL MODE")
            self.mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ec4899;
                    color: #ffffff;
                    font-size: 11px;
                    font-weight: bold;
                    border: none;
                    border-radius: 8px;
                }
            """)
            self.notice_box.setStyleSheet("""
                QFrame {
                    background-color: rgba(239, 68, 68, 0.2);
                    border-left: 3px solid #ef4444;
                    border-radius: 10px;
                }
            """)
            self.notice_title.setText("MANUAL OVERRIDE ACTIVE")
            self.notice_title.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 11px;")
            self.notice_body.setText("Automated safety triggers OFF. Manually control motor relay.")
            
            self.motor_frame.setEnabled(True)
        else:
            self.mode_btn.setText("AUTOMATIC MODE")
            self.mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0284c7;
                    color: #ffffff;
                    font-size: 11px;
                    font-weight: bold;
                    border: none;
                    border-radius: 8px;
                }
            """)
            self.notice_box.setStyleSheet("""
                QFrame {
                    background-color: rgba(2, 132, 199, 0.2);
                    border-left: 3px solid #0284c7;
                    border-radius: 10px;
                }
            """)
            self.notice_title.setText("AUTOMATED SAFETY ENGINE ACTIVE")
            self.notice_title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
            self.notice_body.setText(f"Automated triggers activate motor if PM2.5 > {thresh} µg/m³.")
            
            self.motor_frame.setEnabled(False)

        if motor:
            self.motor_btn.setText("RELAY: ON")
            self.motor_btn.setStyleSheet("""
                QPushButton {
                    background-color: #22c55e;
                    color: #ffffff;
                    font-size: 11px;
                    font-weight: bold;
                    border: none;
                    border-radius: 8px;
                }
            """)
        else:
            self.motor_btn.setText("RELAY: OFF")
            self.motor_btn.setStyleSheet("""
                QPushButton {
                    background-color: #334155;
                    color: #94a3b8;
                    font-size: 11px;
                    font-weight: bold;
                    border: none;
                    border-radius: 8px;
                }
            """)
