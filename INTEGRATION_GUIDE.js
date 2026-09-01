/*
 * INTEGRATION GUIDE
 * Motor Bearing Fault Detection System - Dashboard Integration Points
 * 
 * This file documents how the dashboard integrates with other team members'
 * firmware, algorithms, and alerting systems.
 */

// ============================================================================
// SECTION 1: ESP32 FIRMWARE INTEGRATION (Member 2)
// ============================================================================

/*
EXPECTED TELEMETRY FLOW:

1. ESP32 collects raw audio samples from INMP441 MEMS microphone
2. FFT processing (delegated to Member 3) converts to frequency spectrum
3. Anomaly detection scores the bearing condition
4. ESP32 sends WebSocket packet to dashboard every 500ms

TELEMETRY PACKET FORMAT (JSON over WebSocket):
─────────────────────────────────────────────────────────────────────────────

{
  "timestamp": "2024-01-15T14:30:45.123Z",     // ISO 8601 timestamp
  "peakFreq": 4200.5,                          // Hz (dominant frequency)
  "frequencySpectrum": [                       // 256 dB values
    23.4, 24.1, 25.2, 22.8, ..., 21.5
  ],
  "anomalyScore": 65.3,                        // Confidence 0-100%
  "status": "WARNING",                         // HEALTHY|WARNING|CRITICAL
  "noiseFloor": 34.2,                          // Ambient noise dB
  "sampleRate": 16000,                         // Hz (informational)
  "fftSize": 512,                              // Samples (informational)
  "rawPeakAmplitude": 0.85,                    // Optional: 0.0-1.0
  "motorRpm": 1425.0                           // Optional: Motor speed
}

FREQUENCY ARRAY REQUIREMENTS:
- Exactly 256 elements (or update FFT_SIZE in dashboard)
- Values represent dB (0-120 range recommended)
- Index 0 = 0 Hz, Index 255 = 8000 Hz (Nyquist frequency)
- Calculation: Frequency = (index / 256) * 8000

EXAMPLE C++ CODE FOR ESP32:
─────────────────────────────────────────────────────────────────────────────

void sendTelemetry(float peakFreq, float* spectrum, float anomalyScore) {
  // Create JSON document
  StaticJsonDocument<4096> doc;
  
  doc["timestamp"] = getCurrentTimestamp();
  doc["peakFreq"] = peakFreq;
  doc["anomalyScore"] = anomalyScore;
  doc["noiseFloor"] = calibrationNoiseFloor;
  
  // Add 256-element frequency spectrum
  JsonArray specArray = doc.createNestedArray("frequencySpectrum");
  for (int i = 0; i < 256; i++) {
    specArray.add(spectrum[i]);
  }
  
  // Determine status based on anomaly score and frequency
  if (anomalyScore >= 80) {
    doc["status"] = "CRITICAL";
  } else if (peakFreq > 3000 || anomalyScore >= 40) {
    doc["status"] = "WARNING";
  } else {
    doc["status"] = "HEALTHY";
  }
  
  // Serialize to string
  String payload;
  serializeJson(doc, payload);
  
  // Send over WebSocket
  webSocket.sendTXT(payload);
}

COMMANDS FROM DASHBOARD (to ESP32):
─────────────────────────────────────────────────────────────────────────────

1. Calibration Request:
   {"command": "calibrate", "duration": 3000}
   
   Action: Sample ambient noise for 3 seconds, update noiseFloor threshold
   Response: Send normal telemetry with updated noiseFloor
   
   Example C++ handler:
   if (doc["command"] == "calibrate") {
     int duration = doc["duration"];
     calibrateAmbienceNoise(duration);  // Your calibration function
   }

2. Alert Trigger:
   {"command": "alert", "message": "...", "severity": "critical"}
   
   Action: Trigger Telegram bot to send alert (Member 5)
   Implementation: Pass to Telegram integration function
   
   Example C++ handler:
   if (doc["command"] == "alert") {
     String message = doc["message"];
     String severity = doc["severity"];
     sendTelegramAlert(message, severity);
   }

*/

// ============================================================================
// SECTION 2: FFT & ANOMALY DETECTION INTEGRATION (Member 3)
// ============================================================================

/*
FREQUENCY SPECTRUM REQUIREMENTS:

1. Input: 512-sample raw audio buffer from INMP441
2. Process: FFT analysis (using arduinoFFT library)
3. Output: 256-bin frequency spectrum (0-8000 Hz)

DASHBOARD USES:
- Displays real-time frequency spectrum in chart
- Color-codes three bands:
  * Green (Healthy): 0-3000 Hz (normal motor operation)
  * Orange (Warning): 3000-8000 Hz (friction zone - bearing degradation)
  * Red (Critical): 8000+ Hz (severe anomaly)

ANOMALY SCORE ALGORITHM:
─────────────────────────────────────────────────────────────────────────────

The dashboard expects an anomaly score (0-100%) that represents the
confidence that a bearing fault exists. This typically combines:

1. Friction Band Energy (3-8 kHz):
   - Integrate frequency spectrum from 3000-8000 Hz
   - Compare to ambient noise floor
   - If significantly elevated → higher score

2. Peak Frequency Location:
   - If peak is in friction band → higher score
   - If peak in normal band → lower score

3. Spectral Distribution:
   - Narrow peaks → bearing degradation patterns
   - Broadband noise → normal operation

EXAMPLE CALCULATION:
   anomalyScore = (frictionBandEnergy / noiseFloor) * 0.7 +
                  (peakInFrictionBand ? 0.3 : 0.0)

DYNAMIC THRESHOLD (3-Second Calibration):
─────────────────────────────────────────────────────────────────────────────

When user clicks "Calibrate Ambient Noise":
1. ESP32 receives: {"command": "calibrate", "duration": 3000}
2. For 3 seconds, sample only the motor with NO artificial friction
3. Measure the peak ambient friction band (3-8 kHz)
4. Set threshold = peak + 25% margin
5. Send updated noiseFloor in next telemetry packet

This makes the system adapt to different environments!

*/

// ============================================================================
// SECTION 3: TELEGRAM ALERTING INTEGRATION (Member 5)
// ============================================================================

/*
ALERT FLOW:

1. Dashboard detects status change to CRITICAL
   → Sends command: {"command": "alert", ...}
   → Over WebSocket to ESP32

2. ESP32 receives alert command
   → Calls your Telegram Bot API integration
   → Sends message to Telegram Chat

3. All 6 team members receive instant phone notification
   → Alert includes timestamp, peak frequency, anomaly score
   → Links to live dashboard for detailed view

DASHBOARD COMMANDS TO ESP32:
─────────────────────────────────────────────────────────────────────────────

Critical Alert Trigger:
{
  "command": "alert",
  "message": "⚠️ CRITICAL: Motor bearing anomaly detected! Peak frequency: 5200 Hz, Anomaly score: 92%",
  "severity": "critical",
  "timestamp": "2024-01-15T14:35:22.456Z"
}

Expected Response (in next telemetry):
- Status changes to CRITICAL
- anomalyScore increases
- frequencySpectrum shows elevated friction band

EXPECTED TELEGRAM MESSAGE FORMAT:
─────────────────────────────────────────────────────────────────────────────

🚨 CRITICAL BEARING FAULT ALERT! 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Time: 2024-01-15 14:35:22 UTC
Peak Frequency: 5200 Hz
Anomaly Score: 92%
Status: CRITICAL ANOMALY DETECTED

⚡ Immediate Action Required!
📊 View Dashboard: http://192.168.1.XX:8000

COORDINATION WITH MEMBER 5:
- Confirm Bot Token and Chat ID
- Test with test alert before live demo
- Verify latency (should be <1 second)
- Include current dashboard URL in messages

*/

// ============================================================================
// SECTION 4: QA & DEMO INTEGRATION (Member 6)
// ============================================================================

/*
TESTING CHECKLIST:

Status Transitions Test:
□ Motor off, idle: Status = HEALTHY (green)
□ Motor running smoothly: Status = HEALTHY
□ Light bearing friction: Status = WARNING (orange)
□ Heavy bearing friction: Status = CRITICAL (red)

Frequency Response Test:
□ Healthy: Peak frequency 1000-2000 Hz
□ Friction: Peak frequency 3000-6000 Hz
□ Severe: Peak frequency 6000-8000+ Hz

Event Logging Test:
□ Every status change creates event log entry
□ Peak frequency values recorded accurately
□ Anomaly scores increase progressively
□ Timestamps are sequential

Calibration Test:
□ Click "Calibrate Ambient Noise" button
□ Wait 3 seconds for completion
□ Verify noiseFloor updates in metrics
□ Confirm threshold changes detection sensitivity

Telegram Alert Test:
□ Trigger CRITICAL status
□ Telegram message arrives in <1 second
□ Message includes timestamp and current values
□ Alert doesn't spam (one per state change)

Mobile Responsiveness Test:
□ Dashboard works on tablet (landscape/portrait)
□ Dashboard works on smartphone
□ Chart resizes correctly
□ Buttons are touch-friendly

Demo Sequence Practice:
1. Start with motor off (HEALTHY)
2. Gradually introduce friction (CRITICAL)
3. Watch status badge change colors
4. See event log populate
5. Verify Telegram alert received
6. Export data to CSV
7. Reset and repeat 2-3 times

*/

// ============================================================================
// SECTION 5: DATA FLOW DIAGRAM
// ============================================================================

/*
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────────────────┐
                         │   INMP441 MICROPHONE     │
                         │  (Physical Audio Input)  │
                         └──────────┬───────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │  I2S AUDIO CAPTURE (Member 2)  │
                    │  512-sample buffer @ 16kHz     │
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                   ┌──────────────────────────────────┐
                   │  FFT PROCESSING (Member 3)       │
                   │  256-bin frequency spectrum      │
                   │  Anomaly score calculation       │
                   └────────────┬─────────────────────┘
                                │
                ┌───────────────┴────────────────┐
                │                                │
                ▼                                ▼
    ┌──────────────────────────┐   ┌──────────────────────────┐
    │   STATUS DETERMINATION   │   │  TELEGRAM ALERT (Mem 5)  │
    │  HEALTHY/WARNING/CRITICAL│   │  SEND NOTIFICATION       │
    │                          │   └──────────────────────────┘
    └────────────┬─────────────┘
                 │
                 ▼
    ┌──────────────────────────────────────┐
    │   WebSocket Telemetry Packet (JSON)  │
    │  - peakFreq                          │
    │  - frequencySpectrum[256]            │
    │  - anomalyScore                      │
    │  - status                            │
    │  - noiseFloor                        │
    └────────────┬─────────────────────────┘
                 │
              :8080
                 │
                 ▼
    ┌──────────────────────────────────────┐
    │    DASHBOARD (Member 4) ← You!       │
    │  - Real-time chart visualization     │
    │  - Status badge updates              │
    │  - Event logging                     │
    │  - Calibration triggers              │
    │  - Data export                       │
    └──────────────────────────────────────┘
                 │
                 ▼ (Commands)
    ┌──────────────────────────────────────┐
    │  ESP32 Firmware (Member 2)           │
    │  - Receive calibration request       │
    │  - Receive alert triggers            │
    │  - Update noise floor                │
    │  - Send Telegram messages            │
    └──────────────────────────────────────┘

*/

// ============================================================================
// SECTION 6: TESTING SCENARIOS
// ============================================================================

/*
SCENARIO 1: Real ESP32 With Live Motor
─────────────────────────────────────────────────────────────────────────────

1. Hardware is assembled and wired (Member 1)
2. ESP32 firmware is flashed (Member 2)
3. FFT and anomaly detection code is running (Member 3)
4. WebSocket server is broadcasting on port 8080
5. You run dashboard and connect

Expected: Real-time frequency data and status updates

Test Steps:
- Start motor in healthy state → Watch HEALTHY status (green)
- Apply gentle friction to shaft → Watch WARNING status (orange)
- Apply heavy friction to shaft → Watch CRITICAL status (red)
- Remove friction → Watch status revert to HEALTHY
- Export log to verify all events recorded

SCENARIO 2: Test Without Real Hardware (Demo Mode)
─────────────────────────────────────────────────────────────────────────────

1. Run test_server.py (simulates realistic bearing degradation)
2. Start dashboard on http://localhost:8000
3. Watch simulated progression:
   - 0-60s: HEALTHY with ~5% anomaly score
   - 60-120s: WARNING with increasing score
   - 120-180s: CRITICAL with >85% score
   - 180s+: Sustained CRITICAL state

Use this to verify all UI features work before hardware is ready!

SCENARIO 3: Multi-Client Dashboard
─────────────────────────────────────────────────────────────────────────────

Multiple team members viewing same dashboard simultaneously:

1. Run test_server.py (supports multiple WebSocket clients)
2. Open dashboard in different browser windows/tabs
3. All clients receive identical telemetry
4. Event log syncs across clients
5. Each client can export independently

This is perfect for live expo demo - project team watches same display!

*/

// ============================================================================
// SECTION 7: DEPLOYMENT CHECKLIST
// ============================================================================

/*
PRE-DEMO VERIFICATION:

Hardware (Member 1):
□ INMP441 wired to ESP32 (pins 32, 25, 33)
□ 5V motor connected with switch
□ All connections stable on breadboard
□ Demo setup cleanly mounted

Firmware (Member 2):
□ ESP32 connects to WiFi
□ WebSocket server runs on :8080
□ Telemetry packets sent every 500ms
□ JSON format matches specification
□ Accepts calibration commands

DSP/FFT (Member 3):
□ FFT processes 512-sample buffers correctly
□ Frequency spectrum has 256 bins
□ Anomaly score ranges 0-100%
□ Status logic works: HEALTHY → WARNING → CRITICAL

Dashboard (Member 4 - You!):
□ HTML/CSS/JS files in same directory
□ HTTP server running on :8000
□ Dashboard loads without errors
□ All UI elements render correctly
□ Keyboard shortcuts work (Alt+C, Alt+E, Alt+R)
□ Export to CSV creates valid file
□ Mobile responsive layout works

Telegram Alerts (Member 5):
□ Bot token valid and saved
□ Chat ID or group ID correct
□ Alerts deliver in <1 second
□ Message format is clear

Demo Sequence (Member 6):
□ Motor starts and stops reliably
□ Status badge changes smoothly
□ Event log has 5+ test entries
□ Charts update in real-time
□ Team can see same dashboard
□ Backup laptop ready in case of issues

DEMO DAY RUNSHEET:

1. "Starting up system..." (Boot ESP32, load dashboard)
2. "Motor idle - system healthy" (Show green status)
3. "Introducing bearing friction..." (Apply friction, watch orange)
4. "Critical fault detected!" (Full friction, red status)
5. "Telegram alert sent to team" (Show notification on phone)
6. "Exporting log data..." (CSV download with all events)
7. "System resets" (Dashboard clears, repeats cycle)

*/

console.log("✅ Integration Guide loaded. See README.md and this file for details.");
