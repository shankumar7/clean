"""
Tab 2: System Controls, Relay Motor Override & Safety Threshold Settings.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QSpinBox, QSlider
)
from PyQt6.QtCore import Qt


class ControlTab(QWidget):
    def __init__(self, monitor_engine, parent=None):
        super().__init__(parent)
        self.monitor = monitor_engine
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # Title
        title_lbl = QLabel("SYSTEM CONTROL & SAFETY THRESHOLDS")
        title_lbl.setStyleSheet("color: #38bdf8; font-size: 14px; font-weight: bold; letter-spacing: 1px;")
        main_layout.addWidget(title_lbl)
        
        # Notice Box
        self.notice_box = QFrame()
        self.notice_box.setStyleSheet("""
            QFrame {
                background-color: rgba(2, 132, 199, 0.2);
                border-left: 4px solid #0284c7;
                border-radius: 12px;
            }
        """)
        notice_layout = QVBoxLayout(self.notice_box)
        notice_layout.setContentsMargins(16, 12, 16, 12)
        
        self.notice_title = QLabel("AUTOMATED SAFETY ENGINE ACTIVE")
        self.notice_title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 13px;")
        
        self.notice_body = QLabel("The system automatically runs the motor relay when PM2.5 goes over threshold limit.")
        self.notice_body.setStyleSheet("color: #e2e8f0; font-size: 12px;")
        self.notice_body.setWordWrap(True)
        
        notice_layout.addWidget(self.notice_title)
        notice_layout.addWidget(self.notice_body)
        main_layout.addWidget(self.notice_box)
        
        # Section 1: System Mode Selector (AUTO / MANUAL)
        mode_frame = QFrame()
        mode_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
            }
        """)
        mode_layout = QHBoxLayout(mode_frame)
        mode_layout.setContentsMargins(20, 16, 20, 16)
        
        mode_info = QVBoxLayout()
        mode_lbl = QLabel("System Mode Override")
        mode_lbl.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        mode_sub = QLabel("Switch between automated safety control and manual user override.")
        mode_sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        mode_info.addWidget(mode_lbl)
        mode_info.addWidget(mode_sub)
        
        mode_layout.addLayout(mode_info, stretch=1)
        
        self.mode_btn = QPushButton("AUTOMATIC MODE")
        self.mode_btn.setMinimumHeight(44)
        self.mode_btn.setMinimumWidth(160)
        self.mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_btn.clicked.connect(self._toggle_mode)
        mode_layout.addWidget(self.mode_btn)
        
        main_layout.addWidget(mode_frame)
        
        # Section 2: Relay Motor Control (Manual Only)
        self.motor_frame = QFrame()
        self.motor_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
            }
        """)
        motor_layout = QHBoxLayout(self.motor_frame)
        motor_layout.setContentsMargins(20, 16, 20, 16)
        
        motor_info = QVBoxLayout()
        motor_lbl = QLabel("Manual Motor Relay Control")
        motor_lbl.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        self.motor_sub = QLabel("Directly trigger GPIO 23 active-LOW relay pin (Active in MANUAL mode only).")
        self.motor_sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        motor_info.addWidget(motor_lbl)
        motor_info.addWidget(self.motor_sub)
        
        motor_layout.addLayout(motor_info, stretch=1)
        
        self.motor_btn = QPushButton("MOTOR OFF")
        self.motor_btn.setMinimumHeight(44)
        self.motor_btn.setMinimumWidth(160)
        self.motor_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.motor_btn.clicked.connect(self._toggle_motor)
        motor_layout.addWidget(self.motor_btn)
        
        main_layout.addWidget(self.motor_frame)
        
        # Section 3: Threshold Limit Adjuster
        thresh_frame = QFrame()
        thresh_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
            }
        """)
        thresh_layout = QHBoxLayout(thresh_frame)
        thresh_layout.setContentsMargins(20, 16, 20, 16)
        
        thresh_info = QVBoxLayout()
        thresh_lbl = QLabel("Auto Mode PM2.5 Safety Threshold")
        thresh_lbl.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        thresh_sub = QLabel("Set PM2.5 concentration level that automatically triggers motor relay.")
        thresh_sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        thresh_info.addWidget(thresh_lbl)
        thresh_info.addWidget(thresh_sub)
        
        thresh_layout.addLayout(thresh_info, stretch=1)
        
        self.spinbox = QSpinBox()
        self.spinbox.setRange(20, 500)
        self.spinbox.setSingleStep(10)
        self.spinbox.setValue(200)
        self.spinbox.setSuffix(" µg/m³")
        self.spinbox.setMinimumHeight(40)
        self.spinbox.setMinimumWidth(140)
        self.spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #0f172a;
                color: #ffffff;
                border: 2px solid #38bdf8;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.spinbox.valueChanged.connect(self._threshold_changed)
        thresh_layout.addWidget(self.spinbox)
        
        main_layout.addWidget(thresh_frame)
        main_layout.addStretch()

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
                    font-size: 13px;
                    font-weight: bold;
                    border: none;
                    border-radius: 12px;
                }
            """)
            self.notice_box.setStyleSheet("""
                QFrame {
                    background-color: rgba(239, 68, 68, 0.2);
                    border-left: 4px solid #ef4444;
                    border-radius: 12px;
                }
            """)
            self.notice_title.setText("MANUAL OVERRIDE ACTIVE")
            self.notice_title.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 13px;")
            self.notice_body.setText("Automated safety safeguards are OFF. You must manually control the motor relay.")
            
            self.motor_frame.setEnabled(True)
            self.motor_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(30, 41, 59, 0.7);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 16px;
                }
            """)
        else:
            self.mode_btn.setText("AUTOMATIC MODE")
            self.mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0284c7;
                    color: #ffffff;
                    font-size: 13px;
                    font-weight: bold;
                    border: none;
                    border-radius: 12px;
                }
            """)
            self.notice_box.setStyleSheet("""
                QFrame {
                    background-color: rgba(2, 132, 199, 0.2);
                    border-left: 4px solid #0284c7;
                    border-radius: 12px;
                }
            """)
            self.notice_title.setText("AUTOMATED SAFETY ENGINE ACTIVE")
            self.notice_title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 13px;")
            self.notice_body.setText(f"Automated safety triggers activate motor if PM2.5 > {thresh} µg/m³.")
            
            self.motor_frame.setEnabled(False)
            self.motor_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(30, 41, 59, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 16px;
                }
            """)

        if motor:
            self.motor_btn.setText("MOTOR RELAY: ON")
            self.motor_btn.setStyleSheet("""
                QPushButton {
                    background-color: #22c55e;
                    color: #ffffff;
                    font-size: 13px;
                    font-weight: bold;
                    border: none;
                    border-radius: 12px;
                }
            """)
        else:
            self.motor_btn.setText("MOTOR RELAY: OFF")
            self.motor_btn.setStyleSheet("""
                QPushButton {
                    background-color: #334155;
                    color: #94a3b8;
                    font-size: 13px;
                    font-weight: bold;
                    border: none;
                    border-radius: 12px;
                }
            """)
