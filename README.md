# Motor Bearing Fault Detection Dashboard

A professional, real-time web dashboard for monitoring motor bearing condition using FFT spectral analysis and anomaly detection algorithms.

## 📋 Overview

This dashboard is designed to work with the ESP32 microcontroller running the bearing fault detection system. It provides:

- **Real-time frequency spectrum visualization** using Chart.js
- **Live status monitoring** (Healthy / Warning / Critical)
- **Peak frequency tracking** in the 0-16 kHz range
- **Anomaly scoring** and confidence levels
- **Dynamic ambient noise calibration** with UI controls
- **Event logging** with timestamp, status, and frequency data
- **Telegram alerting** integration for critical faults
- **Data export** to CSV format
- **WebSocket** real-time communication with ESP32
- **Responsive design** for desktop, tablet, and mobile viewing

## 🚀 Quick Start

### 1. Serve the Dashboard

You can serve this dashboard using any simple HTTP server:

**Using Python 3:**
```bash
python -m http.server 8000
```

**Using Node.js (with http-server):**
```bash
npm install -g http-server
http-server -p 8000
```

**Using VS Code Live Server Extension:**
- Right-click on `index.html` → "Open with Live Server"

Then open your browser to `http://localhost:8000`

### 2. ESP32 WebSocket Connection

The dashboard expects the ESP32 to run a WebSocket server on port 8080. The integrated firmware is in [ESP32_Acoustic_Monitor.ino](ESP32_Acoustic_Monitor.ino).

Install these Arduino libraries before uploading the sketch:

- `arduinoFFT`
- `WebSockets` by Markus Sattler / Links2004
- `ArduinoJson`

After uploading, copy the ESP32 IP address from Serial Monitor and open the dashboard with that address:

```javascript
http://localhost:8000/?esp32=192.168.1.100
```

The ESP32 and the computer running the dashboard must be on the same Wi-Fi network. The sketch sends 256 FFT bins every 500 ms and accepts the dashboard's calibration command.

## 📡 Data Format

### Expected Telemetry Data (JSON from ESP32)

The ESP32 should send telemetry data in this format:

```json
{
  "peakFreq": 4500,
  "frequencySpectrum": [5.2, 4.8, 6.1, ..., 3.9],
  "anomalyScore": 45.5,
  "status": "HEALTHY",
  "noiseFloor": 35.2
}
```

**Field Descriptions:**
- `peakFreq` (number): Dominant frequency in Hz (0-16000)
- `frequencySpectrum` (array): 256-bin frequency spectrum (dB values)
- `anomalyScore` (number): Fault confidence score (0-100%)
- `status` (string): "HEALTHY" | "WARNING" | "CRITICAL"
- `noiseFloor` (number): Current ambient noise level (dB)

### Commands from Dashboard to ESP32

**Calibration Command:**
```json
{
  "command": "calibrate",
  "duration": 3000
}
```

**Alert Trigger Command:**
```json
{
  "command": "alert",
  "message": "CRITICAL: Motor bearing anomaly detected!",
  "severity": "critical"
}
```

## 🎨 Dashboard Features

### Status Badge
- **✓ HEALTHY** (Green): Normal operation, no friction detected
- **⚠ WARNING** (Orange): Elevated friction band (3-8 kHz), monitor closely
- **🚨 CRITICAL** (Red): Severe bearing fault detected, immediate action needed

### Frequency Bands
- **Healthy Band** (0-3,000 Hz): Normal motor operation
- **Friction Band** (3,000-8,000 Hz): Bearing friction alert zone
- **Critical Band** (8,000+ Hz): Severe anomaly indicator

### Real-Time Metrics
1. **Peak Frequency**: Dominant frequency in current spectrum
2. **Ambient Noise Level**: Calibrated background noise threshold
3. **Anomaly Score**: Fault detection confidence (0-100%)
4. **Uptime**: System running duration

### Control Buttons
- **🎯 Calibrate Ambient Noise**: 3-second sampling for dynamic threshold adjustment
- **🔄 Reset Log**: Clear all event history
- **📥 Export Data**: Download event log as CSV

### Event Log
- Displays all recorded anomaly events with timestamp
- Filter by event type (Healthy/Warning/Critical)
- Search by frequency or status
- Individual event deletion
- Statistics panel showing total events and critical count

### Chart Visualization
- Interactive bar chart showing frequency spectrum
- Color-coded bands matching status levels
- Hover tooltips with frequency and amplitude
- Real-time updates without page refresh
- Responsive sizing for all screen sizes

## ⌨️ Keyboard Shortcuts

- **Alt + C**: Trigger calibration
- **Alt + E**: Export data to CSV
- **Alt + R**: Reset event log

## 🔧 Configuration

### Adjust Sample Rate (in script.js)
```javascript
state.sampleRate = 16000; // Change to your ESP32 sample rate
```

### Adjust FFT Size (in script.js)
```javascript
state.fftSize = 512; // Change to match ESP32 FFT size
```

### Change WebSocket Port
```javascript
const wsUrl = `ws://192.168.1.100:8080`; // Use ESP32 IP address
```

## 🧪 Demo Mode

To test the dashboard without an ESP32, enable demo mode in `script.js`:

```javascript
// Uncomment this line (at the bottom of the file)
startPollingMode();
```

This will generate realistic simulated bearing data with random variations.

## 🌐 Deployment

### Local Network (ESP32 on same WiFi)
1. Get ESP32 IP address from Serial Monitor
2. Update dashboard WebSocket URL:
   ```javascript
   const wsUrl = `ws://192.168.1.XX:8080`;
   ```
3. Serve dashboard from your laptop on same network

### Remote Monitoring (with Ngrok or similar)
1. Install ngrok: `brew install ngrok`
2. Expose local server:
   ```bash
   ngrok http 8000
   ```
3. Share the Ngrok URL with team members
4. For WebSocket, use ngrok tunnel for port 8080

## 📱 Browser Compatibility

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Note:** WebSocket requires secure (HTTPS) connection for remote access. Use HTTP for local network.

## 🔐 Security Notes

- This dashboard is designed for **local network use only**
- For production deployment, add:
  - HTTPS/WSS encryption
  - Authentication tokens
  - CORS headers
  - Rate limiting
  - Input validation

## 📊 Data Persistence

Events are stored in browser memory (`state.eventLog` array). To persist data across sessions:

1. Add local storage:
```javascript
// Save event log to localStorage
localStorage.setItem('eventLog', JSON.stringify(state.eventLog));

// Load from localStorage on startup
state.eventLog = JSON.parse(localStorage.getItem('eventLog') || '[]');
```

2. Or connect to a database backend

## 🐛 Troubleshooting

### Dashboard shows "Disconnected"
- Check ESP32 is powered and running
- Verify WebSocket server is listening on port 8080
- Check firewall isn't blocking port 8080
- Verify IP address in WebSocket URL

### No frequency data appearing
- Check `frequencySpectrum` array in telemetry message
- Verify array has 256 elements
- Check values are valid numbers (not NaN)

### Chart not updating
- Open browser console (F12) for error messages
- Check WebSocket message format matches expected JSON
- Verify Chart.js CDN is loaded

### Telegram alerts not working
- Ensure Member 2 (firmware) has Telegram API integration
- Check Bot Token is valid
- Verify Chat ID is correct

## 📚 File Structure

```
Project/
├── index.html          # Main HTML structure
├── style.css          # Complete styling & responsive design
├── script.js          # Dashboard logic & Chart.js integration
└── README.md          # This file
```

## 🎓 Integration with Other Team Members

### With Member 2 (Firmware Lead)
- Expects WebSocket server on port 8080
- Receives status updates and telemetry
- Sends calibration/alert commands

### With Member 3 (DSP/FFT Lead)
- Receives frequency spectrum array (256 bins)
- Uses anomaly classification for status
- Gets anomaly score for confidence calculation

### With Member 5 (Telegram Bot Lead)
- Receives alert trigger from dashboard
- Sends critical alerts to Telegram group
- Integrates ESP32 → Telegram notification pipeline

### With Member 6 (QA & Demo Lead)
- Tests calibration feature
- Verifies status transitions (Healthy→Warning→Critical)
- Validates event log accuracy
- Conducts stress testing with multiple alerts

## 📝 Next Steps

1. **Save dashboard files** to your project folder
2. **Test locally** with demo mode enabled
3. **Configure WebSocket URL** for your ESP32 IP
4. **Coordinate with Member 2** for data format compatibility
5. **Integrate Telegram alerts** with Member 5
6. **Conduct UI testing** with Member 6
7. **Deploy** to local network for live expo demo

## 🎉 Key Deliverables (Member 4)

✅ Clean, responsive single-page dashboard (index.html + CSS)
✅ Chart.js integration for dynamic frequency visualization
✅ Live Status Badge (Green/Red with emoji indicators)
✅ Peak frequency readout and ambient noise display
✅ "Calibrate Ambient Noise" trigger button
✅ Comprehensive Anomaly Event Log with filtering
✅ Professional UI ready for WebSocket/HTTP telemetry
✅ Keyboard shortcuts and data export functionality
✅ Mobile-responsive design for tablets and phones
✅ Full integration with other team roles

---

**Dashboard Version:** 1.0.0  
**Last Updated:** 2024  
**Team:** Bearing Fault Detection Project
#   M o t o r - B e a r i n g - F a u l t - D e t e c t i o n 
 
 