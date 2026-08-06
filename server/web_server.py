"""
Flask Web Server module hosting the project management dashboard & REST API.
"""

import threading
import logging
from flask import Flask, jsonify, request, render_template, send_from_directory
import config

# Suppress verbose Flask logging output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def create_flask_app(monitor_engine):
    app = Flask(__name__, template_folder="templates")

    @app.route("/")
    def handle_root():
        """Main web dashboard matching clean.txt interface."""
        return render_template("index.html")

    # ----- clean.txt Legacy Endpoint Compatibility -----
    @app.route("/data")
    def handle_data():
        return jsonify(monitor_engine.get_state_dict())

    @app.route("/setMode")
    def handle_set_mode_legacy():
        if "manual" in request.args:
            manual = (request.args.get("manual") == "1")
            monitor_engine.set_manual_mode(manual)
        return jsonify(monitor_engine.get_state_dict())

    @app.route("/toggleMotor")
    def handle_toggle_motor_legacy():
        if "state" in request.args:
            state = (request.args.get("state") == "1")
            monitor_engine.set_motor_state(state)
        return jsonify(monitor_engine.get_state_dict())

    # ----- Modern REST API Endpoints -----
    @app.route("/api/data", methods=["GET"])
    def api_get_data():
        return jsonify(monitor_engine.get_state_dict())

    @app.route("/api/mode", methods=["POST"])
    def api_set_mode():
        data = request.get_json(silent=True) or {}
        manual = data.get("manual", False)
        monitor_engine.set_manual_mode(manual)
        return jsonify({"status": "success", "state": monitor_engine.get_state_dict()})

    @app.route("/api/motor", methods=["POST"])
    def api_set_motor():
        data = request.get_json(silent=True) or {}
        state = data.get("state", False)
        success = monitor_engine.set_motor_state(state)
        return jsonify({"status": "success" if success else "rejected", "state": monitor_engine.get_state_dict()})

    @app.route("/api/config", methods=["POST"])
    def api_set_config():
        data = request.get_json(silent=True) or {}
        if "pm25_threshold" in data:
            monitor_engine.set_pm25_threshold(data["pm25_threshold"])
        return jsonify({"status": "success", "state": monitor_engine.get_state_dict()})

    return app


class WebServerThread(threading.Thread):
    def __init__(self, monitor_engine, host=config.SERVER_HOST, port=config.SERVER_PORT):
        super().__init__(daemon=True)
        self.monitor = monitor_engine
        self.host = host
        self.port = port
        self.app = create_flask_app(monitor_engine)

    def run(self):
        print(f"[WebServer] Starting host web server on http://{self.host}:{self.port}")
        # Run Flask server silently
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
