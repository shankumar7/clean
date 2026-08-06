"""
Tab 3: Mobile Remote Web Portal Access & Dynamic QR Code Display.
"""

import socket
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt
from gui.components.qr_widget import QRCodeWidget
import config


def get_network_ip_addresses():
    """Retrieve list of active IP addresses for network interfaces."""
    ip_list = []
    try:
        # Try connecting via UDP socket to discover default routing IP
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
        # Fallback to hostname resolution
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
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # Header
        header_vbox = QVBoxLayout()
        title_lbl = QLabel("MOBILE REMOTE MANAGEMENT PORTAL")
        title_lbl.setStyleSheet("color: #38bdf8; font-size: 14px; font-weight: bold; letter-spacing: 1px;")
        sub_lbl = QLabel("Scan the QR code below with any smartphone or tablet on the same Wi-Fi / Hotspot to open the Web Dashboard.")
        sub_lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
        sub_lbl.setWordWrap(True)
        
        header_vbox.addWidget(title_lbl)
        header_vbox.addWidget(sub_lbl)
        main_layout.addLayout(header_vbox)
        
        # Central Section: QR Code & IP Details
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }
        """)
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(24, 20, 24, 20)
        
        # Left side: Dynamic QR Code Widget
        initial_url = f"http://{self.ip_addresses[0]}:{config.SERVER_PORT}"
        self.qr_widget = QRCodeWidget(url=initial_url)
        content_layout.addWidget(self.qr_widget, stretch=1)
        
        # Right side: Network connection instructions & URL dropdown
        info_vbox = QVBoxLayout()
        info_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_vbox.setSpacing(12)
        
        step1_lbl = QLabel("📱 <b>Step 1:</b> Connect smartphone to same Wi-Fi / Hotspot.")
        step1_lbl.setStyleSheet("color: #f8fafc; font-size: 13px;")
        
        step2_lbl = QLabel("📷 <b>Step 2:</b> Open phone camera and scan the QR code.")
        step2_lbl.setStyleSheet("color: #f8fafc; font-size: 13px;")
        
        step3_lbl = QLabel("🌐 <b>Step 3:</b> Manage air quality & manual controls remotely.")
        step3_lbl.setStyleSheet("color: #f8fafc; font-size: 13px;")
        
        info_vbox.addWidget(step1_lbl)
        info_vbox.addWidget(step2_lbl)
        info_vbox.addWidget(step3_lbl)
        
        # Interface Selector Box
        ip_box = QVBoxLayout()
        ip_box.setSpacing(4)
        ip_lbl = QLabel("Active Host Web Server URL:")
        ip_lbl.setStyleSheet("color: #38bdf8; font-size: 12px; font-weight: bold;")
        
        self.ip_combo = QComboBox()
        self.ip_combo.setMinimumHeight(36)
        self.ip_combo.setStyleSheet("""
            QComboBox {
                background-color: #0f172a;
                color: #ffffff;
                border: 2px solid #38bdf8;
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.ip_combo.currentIndexChanged.connect(self._on_ip_selected)
        self._populate_ips()
        
        ip_box.addWidget(ip_lbl)
        ip_box.addWidget(self.ip_combo)
        
        # Refresh Network IP button
        self.refresh_btn = QPushButton("🔄 Refresh Network Interfaces")
        self.refresh_btn.setMinimumHeight(36)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #38bdf8;
                border: 1px solid #38bdf8;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #38bdf8;
                color: #0f172a;
            }
        """)
        self.refresh_btn.clicked.connect(self._refresh_network_ips)
        ip_box.addWidget(self.refresh_btn)
        
        info_vbox.addLayout(ip_box)
        content_layout.addLayout(info_vbox, stretch=1)
        
        main_layout.addWidget(content_frame, stretch=1)

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
