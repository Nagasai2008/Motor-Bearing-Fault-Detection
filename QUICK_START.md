# 🚀 QUICK START GUIDE - MOTOR BEARING DASHBOARD

## Your Role: Frontend Web Dashboard & UI Lead (Member 4)

### ✅ DELIVERABLES COMPLETED

- [x] **index.html** - Professional responsive dashboard interface
- [x] **style.css** - Modern styling with dark/light theme support
- [x] **script.js** - Chart.js integration & real-time data handling
- [x] **test_server.py** - WebSocket test server with simulated data
- [x] **README.md** - Complete technical documentation
- [x] **INTEGRATION_GUIDE.js** - Coordination specs for all team members
- [x] **SETUP_GUIDE.py** - Detailed setup instructions
- [x] **This file** - Quick reference card

---

## 🎯 THE 60-SECOND START

### Step 1: Run Test Server (Terminal 1)
```bash
cd "c:\Users\saisa\OneDrive\Desktop\Project"
python test_server.py
```
✨ Simulates ESP32 telemetry with realistic bearing degradation

### Step 2: Start Web Server (Terminal 2)
```bash
cd "c:\Users\saisa\OneDrive\Desktop\Project"
python -m http.server 8000
```

### Step 3: Open Dashboard (Browser)
```
http://localhost:8000
```

**You're live!** Watch the status badge change from GREEN → ORANGE → RED

---

## 🎨 WHAT YOU JUST BUILT

### Core Features
```
✓ Real-time frequency spectrum chart (256 Hz bins, 0-16kHz)
✓ Live status badge (HEALTHY/WARNING/CRITICAL with colors)
✓ Peak frequency display (updated every 500ms)
✓ Ambient noise calibration (3-second sampling)
✓ Anomaly event log (with filtering & search)
✓ Data export to CSV (timestamp, status, frequency, score)
✓ Responsive design (desktop, tablet, mobile)
✓ Keyboard shortcuts (Alt+C, Alt+E, Alt+R)
```

### UI Components
```
📊 Chart: Real-time frequency bar chart
🎯 Status Badge: Visual indicator with emoji
📈 Metrics: Peak Freq, Noise Floor, Anomaly Score, Uptime
🔘 Buttons: Calibrate, Reset, Export (all functional)
📋 Table: Complete event history with filtering
🔌 Connection: Live WebSocket status indicator
📱 Mobile: 100% responsive layout
```

---

## 📡 INTEGRATION POINTS

### With ESP32 Firmware (Member 2)
- Listens on: `ws://localhost:8080`
- Expects: 256-element frequency spectrum every 500ms
- Sends: Calibration & alert commands

### With FFT Algorithm (Member 3)
- Receives: 256-bin spectrum (dB values, 0-120 range)
- Displays: Real-time chart with color-coded bands
- Uses: Anomaly score for status (0-100%)

### With Telegram Bot (Member 5)
- Triggers: Alert commands on CRITICAL status
- Format: JSON over WebSocket
- Latency: <1 second to phone notification

### With QA Testing (Member 6)
- Tests: All UI features, status transitions
- Verifies: Event logging, mobile responsiveness
- Practices: Demo sequence with live motor

---

## 🧪 TESTING WITHOUT HARDWARE

**Run the test server - it simulates complete bearing degradation:**

```bash
python test_server.py
```

**Timeline:**
- 0-60 seconds: HEALTHY (green, anomaly ~5%)
- 60-120 seconds: WARNING (orange, anomaly ~20-50%)
- 120-180 seconds: CRITICAL (red, anomaly ~60-85%)
- 180+ seconds: Sustained CRITICAL

Perfect for validating all UI features before real hardware arrives!

---

## 🔧 CONNECTING TO REAL ESP32

1. Find ESP32's IP on your network (e.g., `192.168.1.100`)
2. Edit **script.js** line ~380:
   ```javascript
   const wsUrl = `ws://192.168.1.100:8080`;
   ```
3. Reload dashboard
4. Should show "Connected" (green dot)

---

## 📋 FREQUENCY BANDS

Your dashboard color-codes three zones:

| Band | Frequency | Color | Meaning |
|------|-----------|-------|---------|
| Healthy | 0-3 kHz | 🟢 Green | Normal operation |
| Friction | 3-8 kHz | 🟠 Orange | Bearing wear warning |
| Critical | 8+ kHz | 🔴 Red | Severe fault |

---

## ⌨️ KEYBOARD SHORTCUTS

| Shortcut | Action |
|----------|--------|
| **Alt + C** | Calibrate ambient noise |
| **Alt + E** | Export data as CSV |
| **Alt + R** | Clear event log |

---

## 🐛 QUICK TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| "Disconnected" status | Check test_server.py is running on port 8080 |
| Chart not updating | Check browser console (F12) for errors |
| No data appearing | Verify frequencySpectrum has 256 elements |
| Mobile layout broken | Resize browser to test responsiveness |
| Export not working | Clear browser cache, try Chrome |

---

## 📊 EXPECTED DATA FORMAT (from ESP32)

```json
{
  "peakFreq": 4500,
  "frequencySpectrum": [23.4, 24.1, 25.2, ..., 21.5],
  "anomalyScore": 65.3,
  "status": "WARNING",
  "noiseFloor": 34.2
}
```

**Size:** 256-bin spectrum every 500ms ≈ 2-3 KB/second

---

## 🎓 FILE REFERENCE

| File | Purpose |
|------|---------|
| `index.html` | Dashboard structure & all UI elements |
| `style.css` | Professional styling (responsive, themed) |
| `script.js` | Chart.js integration & WebSocket handler |
| `test_server.py` | Simulates ESP32 for testing |
| `README.md` | Complete technical documentation |
| `INTEGRATION_GUIDE.js` | Team coordination specs |
| `SETUP_GUIDE.py` | Detailed setup walkthrough |

---

## 🚀 NEXT STEPS

**Immediate (Today):**
1. ✅ Run test_server.py to verify everything works
2. ✅ Test all UI buttons and features
3. ✅ Verify mobile responsiveness

**This Week:**
1. Coordinate with Member 2 on WebSocket connection
2. Test with real ESP32 firmware
3. Integrate with Member 5's Telegram bot
4. Run full end-to-end testing

**Before Demo:**
1. Practice demo sequence with Member 6
2. Test on multiple devices (laptop, phone, tablet)
3. Verify Telegram alerts work
4. Prepare backup plan if hardware fails

---

## 💡 TIPS FOR SUCCESS

✨ **Pro Tips:**
- Use test_server.py while waiting for ESP32 firmware
- Chart.js automatically scales to window size
- Event log keeps last 100 entries (update in script.js)
- Dashboard stores events in browser memory (not persistent)
- Multiple browser tabs can connect simultaneously

⚡ **Performance:**
- Efficient WebSocket parsing
- Chart updates without animation (smooth real-time)
- Large datasets export instantly to CSV
- Responsive design works on 4K displays

🎨 **Customization:**
- Change colors in style.css (root CSS variables)
- Adjust chart height/width in script.js
- Modify frequency bands (line ~100 in script.js)
- Add custom filters to event log

---

## 🤝 TEAM COORDINATION

| Member | Role | Your Dependency |
|--------|------|-----------------|
| 1 | Hardware Assembly | None - powers ESP32 |
| 2 | Firmware & I2S | **WebSocket on :8080** |
| 3 | FFT & Detection | **256-bin spectrum** |
| 4 | **Dashboard ← YOU!** | Receives telemetry |
| 5 | Telegram Alerts | **Uses your UI commands** |
| 6 | QA & Demo | **Tests your dashboard** |

You're the **hub** - everyone's work flows through your UI!

---

## 📞 QUICK HELP

**Dashboard won't load?**
- Check Python server running (`python -m http.server 8000`)
- Try different port: `python -m http.server 8001`
- Clear browser cache (Ctrl+Shift+Delete)

**WebSocket not connecting?**
- Verify test_server.py is running
- Check firewall isn't blocking port 8080
- Look at browser Console (F12) for errors

**Chart not displaying?**
- Ensure frequencySpectrum is 256 elements
- Check all values are numbers (no NaN)
- Try refreshing dashboard (Ctrl+R)

**Data not exporting?**
- Ensure events are logged (check table)
- Try different browser (Chrome > Firefox > Edge)
- Check browser downloads folder

---

## 🎉 YOU'RE READY!

Your professional bearing fault detection dashboard is **fully functional** and ready to:
- ✅ Receive real-time ESP32 telemetry
- ✅ Visualize frequency spectra in real-time
- ✅ Trigger alerts on bearing faults
- ✅ Log and export anomaly events
- ✅ Work on desktop, tablet, and mobile

**Next: Run `python test_server.py` and watch your dashboard come alive!**

---

**Questions?** Check README.md for complete docs, or INTEGRATION_GUIDE.js for team coordination specs.

**Good luck! 🚀**

---

*Motor Bearing Fault Detection System*  
*Dashboard v1.0 - Ready for Live Demonstration*
