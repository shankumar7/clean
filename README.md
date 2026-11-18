# 🌬️ ESP32 Air Quality Monitor

Real-time air quality monitoring system built with an ESP32 microcontroller and PMS5003 laser particle sensor. Displays PM1.0, PM2.5, and PM10 concentrations on a local LCD and a responsive WiFi web dashboard, with automatic or manual relay-controlled ventilation.

![Platform](https://img.shields.io/badge/Platform-ESP32-blue)
![Sensor](https://img.shields.io/badge/Sensor-PMS5003-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---|---|
| **Real-Time Monitoring** | PM1.0, PM2.5, and PM10 readings updated every second |
| **Web Dashboard** | Responsive single-page UI served over WiFi Access Point — no internet needed |
| **Auto Mode** | Motor/exhaust fan activates automatically when PM2.5 exceeds 200 µg/m³ |
| **Manual Override** | Toggle to manual mode for direct motor control from the dashboard |
| **AQI Classification** | Color-coded badge (Good / Moderate / Poor / Hazardous) with safety precautions |
| **Battery Monitoring** | Live battery percentage with a color-coded progress bar |
| **LCD Display** | 16×2 I2C LCD shows PM2.5 and PM10 at a glance |

---

## 🔧 Hardware

### Components

| Component | Specification |
|---|---|
| Microcontroller | ESP32 DevKit V1 |
| Particle Sensor | Plantower PMS5003 |
| Display | 16×2 I2C LCD (address `0x27`) |
| Relay Module | 5V single-channel, Active LOW |
| Battery Monitor | Voltage divider to GPIO 34 (ADC) |
| Motor / Fan | DC exhaust fan (relay-switched) |

### Wiring Diagram

```
ESP32           PMS5003
─────           ───────
GPIO 16 (RX2) ← TX
GPIO 17 (TX2) → RX
5V             → VCC
GND            → GND

ESP32           I2C LCD
─────           ───────
GPIO 21 (SDA) → SDA
GPIO 22 (SCL) → SCL
5V             → VCC
GND            → GND

ESP32           Relay Module
─────           ────────────
GPIO 23        → IN  (Active LOW)
5V             → VCC
GND            → GND

ESP32           Battery
─────           ───────
GPIO 34 (ADC) ← Voltage Divider Mid-Point
```

---

## 🚀 Getting Started

### Prerequisites

- [Arduino IDE](https://www.arduino.cc/en/software) (2.x recommended) **or** [PlatformIO](https://platformio.org/)
- ESP32 board package installed ([guide](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html))
- Library: **LiquidCrystal_I2C** (install via Library Manager)

### Upload

1. Clone this repository:
   ```bash
   git clone https://github.com/shankumar7/clean.git
   cd clean
   ```
2. Open `clean.ino` in Arduino IDE.
3. Select **Board → ESP32 Dev Module** and the correct **Port**.
4. Click **Upload**.

### Connect

1. On your phone or laptop, connect to WiFi:
   - **SSID:** `ESP32-Air-Monitor`
   - **Password:** `12345678`
2. Open a browser and go to **`http://192.168.4.1`**

---

## 📱 Web Dashboard

The dashboard auto-refreshes every 2 seconds and includes:

- **PM2.5 hero reading** with AQI color badge
- **PM1.0 & PM10** secondary readings
- **Battery level** with color-coded bar
- **Mode switch** — toggle between Automatic and Manual
- **Motor switch** — direct ON/OFF control (enabled only in Manual mode)
- **Context-aware notices** — safety precautions update based on air quality and operating mode

### AQI Thresholds

| PM2.5 (µg/m³) | Level | Badge Color | Auto Motor |
|---|---|---|---|
| 0 – 50 | Good | 🟢 Green | OFF |
| 51 – 100 | Moderate | 🟠 Orange | OFF |
| 101 – 200 | Poor | 🔴 Red | OFF |
| 201+ | Hazardous | 🟤 Dark Red | **ON** |

---

## 📂 Project Structure

```
├── clean.ino          # Main firmware (ESP32 Arduino sketch)
└── README.md          # This file
```

---

## ⚙️ Configuration

These constants in `clean.ino` can be adjusted:

| Constant | Default | Description |
|---|---|---|
| `AP_SSID` | `"ESP32-Air-Monitor"` | WiFi access point name |
| `AP_PASS` | `"12345678"` | WiFi password (min 8 chars) |
| `PM25_THRESHOLD` | `200` | PM2.5 level (µg/m³) that triggers the motor in Auto mode |
| `RELAY_PIN` | `23` | GPIO pin connected to relay IN |
| `BATTERY_PIN` | `34` | ADC pin for battery voltage divider |

> **Note:** Calibrate the `map(rawBat, 2800, 4095, 0, 100)` range in `handleData()` to match your specific voltage divider and battery chemistry.

---

## 🛣️ Roadmap

- [ ] Add OLED display support as an alternative to 16×2 LCD
- [ ] Log historical data to SPIFFS/SD card
- [ ] Add chart visualization on the web dashboard
- [ ] OTA (Over-The-Air) firmware updates
- [ ] MQTT support for integration with Home Assistant

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [Plantower PMS5003 Datasheet](https://www.aqmd.gov/docs/default-source/aq-spec/resources-page/plantower-pms5003-manual_v2-3.pdf)
- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)
- [LiquidCrystal_I2C Library](https://github.com/johnrickman/LiquidCrystal_I2C)
