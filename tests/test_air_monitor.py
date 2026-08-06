"""
Unit tests for Air Quality Monitor core engine and web server API.
"""

import unittest
import json
from core.monitor import AirQualityMonitor
from server.web_server import create_flask_app


class TestAirQualityMonitor(unittest.TestCase):
    def test_monitor_state_initialization(self):
        monitor = AirQualityMonitor(pm25_threshold=200)
        state = monitor.get_state_dict()
        self.assertEqual(state["pm2_5"], 0)
        self.assertEqual(state["motor"], 0)
        self.assertEqual(state["manual"], 0)
        self.assertEqual(state["pm25_threshold"], 200)

    def test_automated_safety_trigger(self):
        monitor = AirQualityMonitor(pm25_threshold=200)
        relay_states = []
        monitor.set_relay_callback(lambda s: relay_states.append(s))

        # PM2.5 = 150 (below threshold) -> Motor OFF
        monitor.update_sensor_data(10, 150, 160)
        self.assertFalse(monitor.motor_state)

        # PM2.5 = 210 (above threshold) -> Motor automatically triggers ON
        monitor.update_sensor_data(20, 210, 220)
        self.assertTrue(monitor.motor_state)
        self.assertTrue(len(relay_states) > 0)
        self.assertTrue(relay_states[-1])

    def test_manual_mode_override(self):
        monitor = AirQualityMonitor(pm25_threshold=200)
        
        # Enable Manual Mode
        monitor.set_manual_mode(True)
        self.assertTrue(monitor.manual_mode)

        # User toggles motor ON manually
        result = monitor.set_motor_state(True)
        self.assertTrue(result)
        self.assertTrue(monitor.motor_state)

        # PM2.5 drops to 10 (Normally motor turns off in AUTO mode, but in MANUAL mode motor stays ON)
        monitor.update_sensor_data(5, 10, 15)
        self.assertTrue(monitor.motor_state)

    def test_flask_web_server_endpoints(self):
        monitor = AirQualityMonitor()
        app = create_flask_app(monitor)
        client = app.test_client()

        # GET /data
        res = client.get("/data")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("pm2_5", data)
        self.assertIn("motor", data)

        # GET /setMode?manual=1
        res = client.get("/setMode?manual=1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["manual"], 1)

        # GET /toggleMotor?state=1
        res = client.get("/toggleMotor?state=1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["motor"], 1)


if __name__ == "__main__":
    unittest.main()
