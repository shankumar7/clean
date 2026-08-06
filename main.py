"""
Main entry point for Raspberry Pi Air Quality Monitor & Host Web Server application.
Unifies GUI Touchscreen Display, Embedded Flask Server, PMS5003 Sensor Reader, and GPIO Relay Controller.
"""

import sys
import signal
import argparse
from core.monitor import AirQualityMonitor
from core.pms5003 import PMS5003Reader
from core.relay import MotorRelayController
from server.web_server import WebServerThread
import config


def parse_arguments():
    parser = argparse.ArgumentParser(description="Raspberry Pi Air Quality Monitor & Host Server")
    parser.add_argument("--port", type=int, default=config.SERVER_PORT, help="Host Web Server Port (default: 5000)")
    parser.add_argument("--serial", type=str, default=config.DEFAULT_SERIAL_PORT, help="UART Serial Port (default: /dev/ttyS0)")
    parser.add_argument("--simulate", action="store_true", help="Force simulated sensor data mode")
    parser.add_argument("--headless", action="store_true", help="Run in headless server mode without GUI")
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.simulate:
        config.FORCE_SIMULATION = True
        
    # ── CRITICAL FIXES FOR RASPBERRY PI OS BOOKWORM ──
    # Bypass qt6ct platform theme loop bug
    import os
    os.environ["QT_QPA_PLATFORMTHEME"] = ""
    os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"
        
    print("=" * 60)
    print("  Raspberry Pi Air Quality Monitor & Host Web Server")
    print("=" * 60)
    
    # CRITICAL: Create QApplication BEFORE any background threads are started
    app = None
    if not args.headless:
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication(sys.argv)
            app.setApplicationName("Air Quality Monitor")
            app.setStyle("Fusion")
        except Exception as e:
            print(f"[GUI] Qt init error: {e}")

    # 1. Initialize State Engine
    monitor_engine = AirQualityMonitor()
    
    # 2. Initialize Hardware Relay Controller
    relay_controller = MotorRelayController(pin=config.RELAY_GPIO_PIN, active_low=config.ACTIVE_LOW_RELAY)
    monitor_engine.set_relay_callback(relay_controller.set_motor)
    
    # 3. Start PMS5003 Hardware / Simulation Sensor Thread
    sensor_thread = PMS5003Reader(monitor_engine, port=args.serial)
    sensor_thread.start()
    
    # 4. Start Embedded Host Web Server (Flask)
    server_thread = WebServerThread(monitor_engine, port=args.port)
    server_thread.start()
    
    # Clean shutdown handler
    def cleanup_signal_handler(sig, frame):
        print("\n[System] Shutting down Air Quality Monitor...")
        sensor_thread.stop()
        relay_controller.cleanup()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, cleanup_signal_handler)
    signal.signal(signal.SIGTERM, cleanup_signal_handler)
    
    # 5. Start GUI or Headless Mode
    if args.headless or app is None:
        print("[System] Running in HEADLESS mode. Press Ctrl+C to stop.")
        signal.pause()
    else:
        try:
            from gui.app import AirMonitorMainWindow
            
            window = AirMonitorMainWindow(monitor_engine)
            window.showFullScreen()
            
            # Use Qt event loop
            exit_code = app.exec()
            sensor_thread.stop()
            relay_controller.cleanup()
            sys.exit(exit_code)
        except Exception as e:
            print(f"[GUI] Could not launch PyQt6 GUI display: {e}")
            print("[GUI] Falling back to headless web server mode. Press Ctrl+C to exit.")
            signal.pause()


if __name__ == "__main__":
    main()
