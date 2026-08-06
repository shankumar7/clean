"""
Tab 3: Mobile Remote Web Portal Access & Dynamic QR Code Display (Optimized for 5" Displays).
"""

import socket
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt
from gui.components.qr_widget import QRCodeWidget
import config


def get_network_ip_addresses():
    """Retrieve list of active IP addresses for network interfaces."""
    ip_list = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
        if primary_ip and primary_ip != "127.0.0.1":
            ip_list.append(primary_ip)
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        host_ips = socket.gethostbyname_ex(hostname)[2]
        for ip in host_ips:
            if ip not in ip_list and not ip.startswith("127."):
                ip_list.append(ip)
    except Exception:
        pass

    if not ip_list:
        ip_list.append("127.0.0.1")
        
    return ip_list


class QRCodeTab(QWidget):
    def __init__(self, monitor_engine, parent=None):
        super().__init__(parent)
        self.monitor = monitor_engine
        self.ip_addresses = get_network_ip_addresses()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(6, 6, 6, 6)
        content_layout.setSpacing(8)
        
        # Header
        title_lbl = QLabel("MOBILE REMOTE MANAGEMENT PORTAL")
        title_lbl.setStyleSheet("color: #38bdf8; font-size: 12px; font-weight: bold; letter-spacing: 0.5px;")
        sub_lbl = QLabel("Scan QR code with smartphone to manage project over local Wi-Fi.")
        sub_lbl.setStyleSheet("color: #94a3b8; font-size: 10px;")
        sub_lbl.setWordWrap(True)
        
        content_layout.addWidget(title_lbl)
        content_layout.addWidget(sub_lbl)
        
        # Central Section
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        card_layout = QHBoxLayout(card_frame)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(10)
        
        # Left side: QR Code Widget (size 160)
        initial_url = f"http://{self.ip_addresses[0]}:{config.SERVER_PORT}"
        self.qr_widget = QRCodeWidget(url=initial_url)
        card_layout.addWidget(self.qr_widget, stretch=0)
        
        # Right side: Instructions & IP selector
        info_vbox = QVBoxLayout()
        info_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_vbox.setSpacing(6)
        
        step1_lbl = QLabel("📱 1. Connect phone to same Wi-Fi.")
        step1_lbl.setStyleSheet("color: #f8fafc; font-size: 11px;")
        
        step2_lbl = QLabel("📷 2. Scan QR code with camera.")
        step2_lbl.setStyleSheet("color: #f8fafc; font-size: 11px;")
        
        step3_lbl = QLabel("🌐 3. Manage project on mobile.")
        step3_lbl.setStyleSheet("color: #f8fafc; font-size: 11px;")
        
        info_vbox.addWidget(step1_lbl)
        info_vbox.addWidget(step2_lbl)
        info_vbox.addWidget(step3_lbl)
        
        ip_lbl = QLabel("Web Server URL:")
        ip_lbl.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold;")
        
        self.ip_combo = QComboBox()
        self.ip_combo.setMinimumHeight(30)
        self.ip_combo.setStyleSheet("""
            QComboBox {
                background-color: #0f172a;
                color: #ffffff;
                border: 1px solid #38bdf8;
                border-radius: 6px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        self.ip_combo.currentIndexChanged.connect(self._on_ip_selected)
        self._populate_ips()
        
        info_vbox.addWidget(ip_lbl)
        info_vbox.addWidget(self.ip_combo)
        
        self.refresh_btn = QPushButton("🔄 Refresh IP")
        self.refresh_btn.setMinimumHeight(28)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #38bdf8;
                border: 1px solid #38bdf8;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10px;
            }
        """)
        self.refresh_btn.clicked.connect(self._refresh_network_ips)
        info_vbox.addWidget(self.refresh_btn)
        
        card_layout.addLayout(info_vbox, stretch=1)
        content_layout.addWidget(card_frame)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def _populate_ips(self):
        self.ip_combo.blockSignals(True)
        self.ip_combo.clear()
        for ip in self.ip_addresses:
            url = f"http://{ip}:{config.SERVER_PORT}"
            self.ip_combo.addItem(url)
        self.ip_combo.blockSignals(False)

    def _on_ip_selected(self, index):
        if index >= 0 and index < len(self.ip_addresses):
            selected_url = f"http://{self.ip_addresses[index]}:{config.SERVER_PORT}"
            self.qr_widget.set_url(selected_url)

    def _refresh_network_ips(self):
        self.ip_addresses = get_network_ip_addresses()
        self._populate_ips()
        if self.ip_addresses:
            selected_url = f"http://{self.ip_addresses[0]}:{config.SERVER_PORT}"
            self.qr_widget.set_url(selected_url)

    def update_ui(self, state):
        pass
