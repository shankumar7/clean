/*
 * ============================================================
 *  ESP32 Air Quality Monitor
 * ============================================================
 *  Hardware:  ESP32 DevKit + PMS5003 + 16x2 I2C LCD + Relay
 *  Features:
 *    - Real-time PM1.0 / PM2.5 / PM10 monitoring via PMS5003
 *    - 16x2 I2C LCD for local display
 *    - WiFi Access Point with responsive Web Dashboard
 *    - Dual-mode relay control (Automatic + Manual override)
 *    - Battery voltage monitoring via ADC
 *
 *  Wiring Summary:
 *    PMS5003 TX  → GPIO 16 (ESP32 RX2)
 *    PMS5003 RX  → GPIO 17 (ESP32 TX2)
 *    Relay IN    → GPIO 23 (Active LOW)
 *    Battery ADC → GPIO 34 (via voltage divider)
 *    LCD SDA     → GPIO 21
 *    LCD SCL     → GPIO 22
 *
 *  Author : Shan Kumar
 *  License: MIT
 * ============================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

/* -------------------- Configuration -------------------- */

// Access Point credentials
const char* AP_SSID = "ESP32-Air-Monitor";
const char* AP_PASS = "12345678";

// I2C LCD (address 0x27, 16 columns, 2 rows)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// PMS5003 on Hardware Serial 2
HardwareSerial pmsSerial(2);
#define PMS_RX_PIN 16
#define PMS_TX_PIN 17

// Relay (Active LOW)
#define RELAY_PIN 23

// Battery voltage divider (ADC input)
#define BATTERY_PIN 34

// Auto-mode PM2.5 threshold (µg/m³)
#define PM25_THRESHOLD 200

// Web server on port 80
WebServer server(80);

/* -------------------- Runtime State -------------------- */

uint16_t pm1_0  = 0;
uint16_t pm2_5  = 0;
uint16_t pm10   = 0;
bool     motorState  = false;   // true = relay energised (motor ON)
bool     manualMode  = false;   // false = Auto, true = Manual override

/* -------------------- PMS5003 Reader -------------------- */

/**
 * Reads one complete 32-byte frame from the PMS5003.
 * Returns true on a valid, checksum-verified frame and
 * updates pm1_0, pm2_5, pm10 globals.
 */
bool readPMS() {
  if (pmsSerial.available() < 32) return false;

  // Sync to frame start bytes 0x42 0x4D
  if (pmsSerial.read() != 0x42) return false;
  if (pmsSerial.read() != 0x4D) return false;

  uint8_t buf[32];
  buf[0] = 0x42;
  buf[1] = 0x4D;

  if (pmsSerial.readBytes(&buf[2], 30) != 30) return false;

  // Verify checksum (sum of bytes 0-29 must equal bytes 30-31)
  uint16_t sum = 0;
  for (int i = 0; i < 30; i++) sum += buf[i];

  uint16_t checksum = (buf[30] << 8) | buf[31];
  if (sum != checksum) return false;

  // Extract standard-atmosphere concentrations (µg/m³)
  pm1_0 = (buf[4] << 8) | buf[5];
  pm2_5 = (buf[6] << 8) | buf[7];
  pm10  = (buf[8] << 8) | buf[9];

  return true;
}

/* -------------------- Web Dashboard (HTML) -------------------- */

const char PAGE[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Air Quality Monitor</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    font-family:'Segoe UI',Arial,sans-serif;
    background:linear-gradient(135deg,#1f4037,#99f2c8);
    display:flex; justify-content:center; align-items:center;
    min-height:100vh; padding:20px;
  }
  .card{
    background:#fff; width:370px; padding:28px; border-radius:16px;
    box-shadow:0 10px 30px rgba(0,0,0,.25); text-align:center;
  }
  .title{font-size:20px;font-weight:700;margin-bottom:8px;color:#333}
  .main-value{font-size:44px;font-weight:700;margin:12px 0}
  .unit{font-size:15px;color:#666}
  .badge{
    display:inline-block;padding:5px 18px;border-radius:20px;
    color:#fff;font-weight:700;font-size:14px;margin-bottom:14px;
  }

  /* Info boxes */
  .info-box{
    padding:12px;border-radius:8px;font-size:13px;
    text-align:left;margin:10px 0;line-height:1.5;
  }
  .info-aqi{background:#f9f9f9;color:#555;border-left:4px solid #ccc}
  .info-mode{background:#edf7ff;color:#333;border-left:4px solid #2196F3}

  /* Data rows */
  .data-row{
    margin:8px 0;font-size:15px;display:flex;
    justify-content:space-between;align-items:center;
  }
  .status-on{color:#4CAF50;font-weight:700}
  .status-off{color:#E53935;font-weight:700}
  .mode-auto{color:#1976D2;font-weight:700}
  .mode-manual{color:#E91E63;font-weight:700}

  /* Battery bar */
  .battery-bar{
    width:100%;height:8px;background:#e0e0e0;border-radius:4px;
    margin-top:4px;overflow:hidden;
  }
  .battery-fill{height:100%;border-radius:4px;transition:width .4s}

  /* Control panel */
  .control-panel{
    margin-top:18px;padding-top:14px;border-top:1px solid #eee;
    display:flex;flex-direction:column;gap:14px;
  }
  .switch-row{display:flex;justify-content:space-between;align-items:center}
  .switch{position:relative;display:inline-block;width:54px;height:28px}
  .switch input{opacity:0;width:0;height:0}
  .slider{
    position:absolute;cursor:pointer;inset:0;
    background:#ccc;transition:.3s;border-radius:34px;
  }
  .slider::before{
    position:absolute;content:"";height:20px;width:20px;
    left:4px;bottom:4px;background:#fff;transition:.3s;border-radius:50%;
  }
  /* Manual mode toggle — pink when active */
  #modeSwitch:checked+.slider{background:#E91E63}
  #modeSwitch:checked+.slider::before{transform:translateX(26px)}
  /* Motor toggle — green when active */
  #motorSwitch:checked+.slider{background:#4CAF50}
  #motorSwitch:checked+.slider::before{transform:translateX(26px)}
  /* Disabled state */
  .disabled-row{opacity:.45;pointer-events:none}
</style>
</head>
<body>
<div class="card">

  <!-- Header -->
  <div class="title">Air Quality Monitor</div>
  <div class="main-value">
    <span id="pm25">--</span> <span class="unit">&micro;g/m&sup3;</span>
  </div>
  <div id="aqi-badge" class="badge" style="background:#999">Loading&hellip;</div>

  <!-- Air-quality precaution -->
  <div class="info-box info-aqi">
    <strong>Air Quality Precautions:</strong>
    <div id="precaution-text">Awaiting sensor data&hellip;</div>
  </div>

  <!-- Mode / operation notice -->
  <div class="info-box info-mode">
    <strong>Operation Status Notice:</strong>
    <div id="mode-precaution-text">Initializing&hellip;</div>
  </div>

  <!-- Sensor readings -->
  <div class="data-row"><span>PM1.0:</span><span><span id="pm1">--</span> &micro;g/m&sup3;</span></div>
  <div class="data-row"><span>PM10:</span><span><span id="pm10">--</span> &micro;g/m&sup3;</span></div>
  <div class="data-row"><span>System Mode:</span><span id="sys-mode">--</span></div>
  <div class="data-row"><span>Motor Status:</span><span id="motor">--</span></div>

  <!-- Battery -->
  <div class="data-row"><span>Battery:</span><span id="bat-pct">--</span></div>
  <div class="battery-bar"><div class="battery-fill" id="bat-bar" style="width:0%;background:#4CAF50"></div></div>

  <!-- Controls -->
  <div class="control-panel">
    <div class="switch-row">
      <strong>Manual Mode Override:</strong>
      <label class="switch">
        <input type="checkbox" id="modeSwitch" onclick="changeMode(this)">
        <span class="slider"></span>
      </label>
    </div>
    <div class="switch-row disabled-row" id="motorCtrlRow">
      <span>Manual Motor Control:</span>
      <label class="switch">
        <input type="checkbox" id="motorSwitch" onclick="toggleMotor(this)">
        <span class="slider"></span>
      </label>
    </div>
  </div>
</div>

<script>
/* --- API helpers --- */
function changeMode(el){
  fetch("/setMode?manual="+(el.checked?1:0))
    .then(r=>r.json()).then(updateUI);
}
function toggleMotor(el){
  fetch("/toggleMotor?state="+(el.checked?1:0))
    .then(r=>r.json()).then(updateUI);
}

/* --- UI refresh --- */
function updateUI(d){
  document.getElementById("pm25").textContent=d.pm2_5;
  document.getElementById("pm1").textContent=d.pm1_0;
  document.getElementById("pm10").textContent=d.pm10;

  // System mode
  var modeText=document.getElementById("sys-mode");
  var modeSwitch=document.getElementById("modeSwitch");
  var motorRow=document.getElementById("motorCtrlRow");
  var modePrecText=document.getElementById("mode-precaution-text");

  if(d.manual===1){
    modeText.textContent="MANUAL";
    modeText.className="mode-manual";
    modeSwitch.checked=true;
    motorRow.className="switch-row";
    modePrecText.innerHTML="<b>Warning:</b> Automatic safety controls are OFF. You must manually manage ventilation.";
  }else{
    modeText.textContent="AUTOMATIC";
    modeText.className="mode-auto";
    modeSwitch.checked=false;
    motorRow.className="switch-row disabled-row";
    modePrecText.innerHTML="<b>Notice:</b> Automatic mode active. The motor engages when PM2.5 exceeds 200 &micro;g/m&sup3;.";
  }

  // Motor state
  var motorText=document.getElementById("motor");
  var motorSwitch=document.getElementById("motorSwitch");
  if(d.motor===1){
    motorText.textContent="ON";  motorText.className="status-on";
    motorSwitch.checked=true;
  }else{
    motorText.textContent="OFF"; motorText.className="status-off";
    motorSwitch.checked=false;
  }

  // Battery
  var bp=d.battery_pct;
  document.getElementById("bat-pct").textContent=bp+"%";
  var bar=document.getElementById("bat-bar");
  bar.style.width=bp+"%";
  bar.style.background=bp>50?"#4CAF50":bp>20?"#FF9800":"#F44336";

  // AQI badge + precautions
  var v=d.pm2_5;
  var b=document.getElementById("aqi-badge");
  var p=document.getElementById("precaution-text");
  if(v<=50){
    b.textContent="Good";     b.style.backgroundColor="#4CAF50";
    p.textContent="Air quality is excellent. Safe for outdoor activities.";
  }else if(v<=100){
    b.textContent="Moderate"; b.style.backgroundColor="#FF9800";
    p.textContent="Acceptable quality. Sensitive individuals should limit prolonged outdoor exertion.";
  }else if(v<=200){
    b.textContent="Poor";     b.style.backgroundColor="#F44336";
    p.textContent="Wear masks outdoors. Sensitive individuals should stay indoors.";
  }else{
    b.textContent="Hazardous";b.style.backgroundColor="#730202";
    p.textContent="Hazardous air! Close all windows, run air filters, and keep the motor running.";
  }
}

// Poll the ESP32 every 2 seconds
setInterval(function(){
  fetch("/data").then(function(r){return r.json()}).then(updateUI);
},2000);
</script>
</body>
</html>
)rawliteral";

/* -------------------- HTTP Route Handlers -------------------- */

/** Serve the main dashboard page. */
void handleRoot() {
  server.send_P(200, "text/html", PAGE);
}

/** Return current sensor + state data as JSON. */
void handleData() {
  int rawBat = analogRead(BATTERY_PIN);
  int batPct = map(rawBat, 2800, 4095, 0, 100);
  batPct = constrain(batPct, 0, 100);

  String json = "{";
  json += "\"pm1_0\":"  + String(pm1_0)                + ",";
  json += "\"pm2_5\":"  + String(pm2_5)                + ",";
  json += "\"pm10\":"   + String(pm10)                 + ",";
  json += "\"motor\":"  + String(motorState  ? 1 : 0)  + ",";
  json += "\"manual\":" + String(manualMode  ? 1 : 0)  + ",";
  json += "\"battery_pct\":" + String(batPct);
  json += "}";

  server.send(200, "application/json", json);
}

/** Switch between Auto and Manual mode. */
void handleSetMode() {
  if (server.hasArg("manual")) {
    manualMode = (server.arg("manual").toInt() == 1);
    // If switching back to Auto, let the auto-logic take over on next loop
  }
  handleData();
}

/** Manually toggle motor (only honoured in Manual mode). */
void handleToggleMotor() {
  if (manualMode && server.hasArg("state")) {
    motorState = (server.arg("state").toInt() == 1);
    digitalWrite(RELAY_PIN, motorState ? LOW : HIGH);  // Active-LOW relay
  }
  handleData();
}

/* -------------------- Setup -------------------- */

void setup() {
  Serial.begin(115200);
  delay(1500);

  // Start WiFi Access Point
  WiFi.softAP(AP_SSID, AP_PASS);
  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());

  // Relay — start OFF (HIGH = relay de-energised)
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);

  // LCD init
  lcd.init();
  lcd.backlight();
  lcd.print("System Starting");

  // PMS5003 serial
  pmsSerial.begin(9600, SERIAL_8N1, PMS_RX_PIN, PMS_TX_PIN);

  // Register HTTP routes
  server.on("/",            handleRoot);
  server.on("/data",        handleData);
  server.on("/setMode",     handleSetMode);
  server.on("/toggleMotor", handleToggleMotor);
  server.begin();
  Serial.println("HTTP server started");

  // Show AP SSID on LCD
  lcd.clear();
  lcd.print("WiFi Ready:");
  lcd.setCursor(0, 1);
  lcd.print(AP_SSID);
}

/* -------------------- Main Loop -------------------- */

void loop() {
  server.handleClient();

  if (readPMS()) {
    // --- Automatic relay control ---
    if (!manualMode) {
      if (pm2_5 > PM25_THRESHOLD) {
        digitalWrite(RELAY_PIN, LOW);   // Motor ON
        motorState = true;
      } else {
        digitalWrite(RELAY_PIN, HIGH);  // Motor OFF
        motorState = false;
      }
    }

    // --- Update LCD ---
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("PM2.5:");
    lcd.print(pm2_5);
    lcd.print(" ug/m3");

    lcd.setCursor(0, 1);
    lcd.print("PM10 :");
    lcd.print(pm10);
    lcd.print(" ug/m3");
  }

  delay(1000);
}
