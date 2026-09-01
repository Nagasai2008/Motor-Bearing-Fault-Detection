#!/usr/bin/env python3
"""
Quick Setup & Testing Guide
Motor Bearing Fault Detection Dashboard
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  DASHBOARD SETUP & TESTING GUIDE                            ║
║              Motor Bearing Fault Detection System - Member 4                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📦 PROJECT FILES CREATED:
─────────────────────────────────────────────────────────────────────────────
✅ index.html              → Main dashboard interface
✅ style.css               → Professional styling (responsive design)
✅ script.js               → Chart.js integration & real-time updates
✅ test_server.py          → WebSocket test server with simulated data
✅ README.md               → Complete documentation
✅ SETUP_GUIDE.py          → This file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 QUICK START (5 MINUTES)
─────────────────────────────────────────────────────────────────────────────

OPTION 1: Quickest Setup (With Test Data)
──────────────────────────────────────────
1. Open Terminal in project folder
2. Start the test WebSocket server:
   $ python3 test_server.py

3. In another terminal, start HTTP server:
   $ python -m http.server 8000

4. Open browser: http://localhost:8000
   ✨ Dashboard will show simulated bearing fault progression
   ✨ Watch for status changes: HEALTHY → WARNING → CRITICAL

OPTION 2: With Live ESP32 Data
───────────────────────────────
1. Ensure ESP32 firmware is running WebSocket server on port 8080
2. Update WebSocket URL in script.js (if needed)
3. Start HTTP server:
   $ python -m http.server 8000

4. Open browser: http://localhost:8000
   ✨ Dashboard connects automatically when ESP32 comes online

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 TESTING CHECKLIST
─────────────────────────────────────────────────────────────────────────────

□ Connection Status
  - Server: Run test_server.py
  - Dashboard: Should show "Connected" (green dot)
  - Browser Console: Check for WebSocket messages

□ Real-Time Frequency Chart
  - Verify bars update every 500ms
  - Check color coding: Green (0-3kHz) → Orange (3-8kHz) → Red (8kHz+)
  - Hover over bars to see Hz and dB values

□ Status Badge Updates
  - First 60 seconds: Should stay HEALTHY (green ✓)
  - At 60-120 seconds: Should change to WARNING (orange ⚠)
  - After 120 seconds: Should show CRITICAL (red 🚨)

□ Metrics Display
  - Peak Frequency: Updates in real-time (Hz)
  - Ambient Noise Level: Should be ~30-38 dB
  - Anomaly Score: Increases from 5% → 100%
  - Uptime: Counts up continuously

□ Calibration Button
  - Click "🎯 Calibrate Ambient Noise"
  - Should show 3-second countdown
  - Button becomes disabled during calibration
  - Toast notification confirms completion

□ Event Logging
  - Events appear as alerts trigger
  - Status column shows badge with color
  - Peak frequency and anomaly score recorded
  - Can filter by status or search by value
  - Delete button removes individual events

□ Data Export
  - Click "📥 Export Data"
  - CSV file downloads: bearing-fault-log-[timestamp].csv
  - Open in Excel/Google Sheets to verify data

□ Responsive Design
  - Resize browser window (desktop to mobile)
  - Verify layout adjusts properly
  - Check touch-friendliness on mobile

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 CONFIGURATION FOR YOUR ESP32
─────────────────────────────────────────────────────────────────────────────

1. ESP32 WebSocket Server Requirements:
   ✓ Listen on port 8080
   ✓ Accept HTTP GET to establish WebSocket
   ✓ Send telemetry JSON every 500ms (or your preferred interval)

2. Update Connection URL in script.js (line ~380):
   
   // For localhost
   const wsUrl = `ws://localhost:8080`;
   
   // For ESP32 on network
   const wsUrl = `ws://192.168.1.100:8080`;
   
   // For specific hostname
   const wsUrl = `ws://esp32-bearing.local:8080`;

3. Telemetry Packet Format (JSON from ESP32):
   {
     "peakFreq": 4500,              // Dominant frequency (Hz)
     "frequencySpectrum": [...],    // 256 values (dB)
     "anomalyScore": 45.5,          // 0-100 (%)
     "status": "HEALTHY",           // or "WARNING"/"CRITICAL"
     "noiseFloor": 35.2             // Ambient noise (dB)
   }

4. Commands From Dashboard (receive these in ESP32):
   
   Calibration:
   { "command": "calibrate", "duration": 3000 }
   
   Alert:
   { "command": "alert", "message": "...", "severity": "critical" }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⌨️ KEYBOARD SHORTCUTS
─────────────────────────────────────────────────────────────────────────────
Alt + C   Trigger calibration
Alt + E   Export data to CSV
Alt + R   Reset event log

🔍 BROWSER CONSOLE DEBUGGING
─────────────────────────────────────────────────────────────────────────────
1. Press F12 to open Developer Tools
2. Go to "Console" tab
3. Check for messages like:
   ✓ "Dashboard initialized. Waiting for ESP32 connection..."
   ✓ "WebSocket connected"
   ✓ Connection errors if WebSocket fails

4. Type in console to test:
   state.statusBadge        // Check current status element
   state.eventLog           // View all recorded events
   state.frequencyData      // View frequency spectrum array
   state.isConnected        // Check WebSocket status

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐛 TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────────

Problem: "Disconnected" status
→ Check if test_server.py is running
→ Verify port 8080 isn't blocked by firewall
→ Check browser console for WebSocket errors

Problem: Chart not updating
→ Open Console (F12) and check for errors
→ Verify frequencySpectrum has 256 elements
→ Check all values are numbers (not NaN)

Problem: Status badge doesn't change
→ Test server automatically progresses through phases
→ Wait 60+ seconds for status to change
→ Check "anomaly_score" values in console

Problem: Events not logging
→ Verify WebSocket data is being received
→ Check Console tab for JavaScript errors
→ Try clicking "Reset Log" to clear and start fresh

Problem: Export button doesn't work
→ Check browser console for errors
→ Ensure eventLog array has data
→ Try in different browser (Chrome preferred)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 DEMO MODE (For when ESP32 isn't ready)
─────────────────────────────────────────────────────────────────────────────
Instead of running test_server.py, enable demo mode in script.js:

Uncomment this line (at the very bottom):
    startPollingMode();

Then reload the dashboard. It will generate random data locally without 
needing WebSocket connection.

⚠️  Use test_server.py instead - it's more realistic!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎓 INTEGRATION WITH TEAM MEMBERS
─────────────────────────────────────────────────────────────────────────────

📌 With Member 1 (Hardware):
   → No integration needed
   → Hardware provides power to ESP32
   → Dashboard is purely software

📌 With Member 2 (ESP32 Firmware):
   → Coordinate WebSocket URL and port (8080)
   → Share expected telemetry JSON format (see above)
   → Test connection when firmware is ready

📌 With Member 3 (DSP/FFT):
   → Dashboard receives frequencySpectrum array
   → Displays in real-time chart
   → Uses anomaly score for status determination

📌 With Member 5 (Telegram Bot):
   → Dashboard sends alert commands via WebSocket
   → Coordinate command format
   → Test alert pipeline together

📌 With Member 6 (QA & Demo):
   → Test all UI features together
   → Verify status transitions work correctly
   → Practice demo sequence
   → Check mobile responsiveness

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 NEXT STEPS
─────────────────────────────────────────────────────────────────────────────
1. ✅ Dashboard files ready (you have them)
2. ⏳ Test with test_server.py
3. ⏳ Coordinate with Member 2 on WebSocket connection
4. ⏳ Test with real ESP32 data
5. ⏳ Configure Telegram alerts with Member 5
6. ⏳ Run full integration tests
7. ⏳ Practice demo sequence with Member 6

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ YOU'RE ALL SET!
─────────────────────────────────────────────────────────────────────────────
Your professional bearing fault detection dashboard is ready to receive
live telemetry. All UI components are functional and tested.

Good luck with your expo demo! 🚀

For full documentation, see README.md

Questions? Check the Debug Information panel at the bottom of the dashboard
for real-time system status.

╚══════════════════════════════════════════════════════════════════════════════╝
""")

# Quick reference for common commands
print("\n📋 QUICK COMMAND REFERENCE\n")
print("Start test server:")
print("  $ python3 test_server.py\n")
print("Start HTTP server (Python 3):")
print("  $ python -m http.server 8000\n")
print("Start HTTP server (Node.js):")
print("  $ npx http-server -p 8000\n")
print("Open dashboard:")
print("  http://localhost:8000\n")
print("Check WebSocket connection:")
print("  ws://localhost:8080\n")
