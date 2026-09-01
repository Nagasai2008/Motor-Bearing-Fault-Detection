#!/usr/bin/env python3
"""
Motor Bearing Fault Detection - WebSocket Test Server
Simulates ESP32 telemetry for dashboard testing

Usage:
    python3 test_server.py

Then open http://localhost:8000 in your browser
WebSocket connection: ws://localhost:8080
"""

import asyncio
import json
import math
import random
from datetime import datetime
import websockets

# Server configuration
WEBSOCKET_PORT = 8080
SAMPLE_RATE = 16000
FFT_SIZE = 512
NUM_BINS = 256

# Motor state
motor_state = {
    "rpm": 1500,
    "peak_freq": 1500,
    "noise_floor": 30.0,
    "anomaly_score": 0.0,
    "status": "HEALTHY",
    "is_fault": False,
    "time_started": datetime.now()
}


def generate_frequency_spectrum(peak_freq, anomaly_score):
    """
    Generate realistic frequency spectrum centered around peak_freq.
    
    Args:
        peak_freq: Dominant frequency in Hz
        anomaly_score: Fault severity (0-100)
    
    Returns:
        List of 256 dB values representing frequency spectrum
    """
    spectrum = []
    for i in range(NUM_BINS):
        # Frequency of this bin (Nyquist = 8000 Hz for 16 kHz sample rate)
        freq = (i / NUM_BINS) * 8000
        
        # Gaussian distribution centered at peak_freq
        center_spread = math.exp(-((freq - peak_freq) ** 2) / (1000 ** 2))
        
        # Base noise floor
        base_noise = 20 + random.gauss(0, 2)
        
        # Harmonics
        harmonics = 0
        for harmonic in range(1, 4):
            harmonic_freq = peak_freq * harmonic
            if harmonic_freq < 8000:
                harmonics += 0.3 * math.exp(-((freq - harmonic_freq) ** 2) / (500 ** 2))
        
        # Anomaly-induced high-frequency content (3-8 kHz band)
        if 3000 <= freq <= 8000:
            anomaly_boost = (anomaly_score / 100.0) * 60 * math.exp(-(freq - 5500) ** 2 / (2000 ** 2))
        else:
            anomaly_boost = 0
        
        # Combine components
        amplitude = base_noise + (center_spread * 50) + (harmonics * 30) + anomaly_boost
        spectrum.append(max(0, min(120, amplitude)))  # Clamp to 0-120 dB
    
    return spectrum


def determine_status(peak_freq, anomaly_score):
    """Determine motor status based on frequency and anomaly score."""
    if anomaly_score >= 80:
        return "CRITICAL"
    elif peak_freq > 3000 or anomaly_score >= 40:
        return "WARNING"
    else:
        return "HEALTHY"


def simulate_motor_behavior():
    """
    Simulate realistic motor bearing behavior with gradual degradation.
    """
    elapsed = (datetime.now() - motor_state["time_started"]).total_seconds()
    
    # Baseline peak frequency drifts slowly
    base_drift = math.sin(elapsed / 30) * 300  # ±300 Hz drift every 30 seconds
    noise_variation = random.gauss(0, 100)
    motor_state["peak_freq"] = 1500 + base_drift + noise_variation
    motor_state["peak_freq"] = max(500, min(3000, motor_state["peak_freq"]))
    
    # Simulate bearing degradation phases
    if elapsed < 60:
        # Phase 1: Healthy operation (0-60s)
        motor_state["anomaly_score"] = random.gauss(5, 3)
        motor_state["noise_floor"] = random.gauss(30, 2)
        motor_state["is_fault"] = False
    
    elif elapsed < 120:
        # Phase 2: Early warning (60-120s) - friction detected
        friction_level = (elapsed - 60) / 60 * 30  # Gradual increase
        motor_state["peak_freq"] = 1500 + random.gauss(0, 100) + friction_level * 100
        motor_state["anomaly_score"] = 20 + random.gauss(friction_level, 5)
        motor_state["noise_floor"] = random.gauss(32, 2)
        motor_state["is_fault"] = False
    
    elif elapsed < 180:
        # Phase 3: Critical warning (120-180s)
        motor_state["peak_freq"] = 3000 + random.gauss(0, 200)
        motor_state["anomaly_score"] = 60 + random.gauss(0, 10)
        motor_state["noise_floor"] = random.gauss(35, 2)
        motor_state["is_fault"] = False
    
    else:
        # Phase 4: Critical fault (180s+)
        motor_state["peak_freq"] = 5000 + random.gauss(0, 500)
        motor_state["anomaly_score"] = min(100, 85 + random.gauss(0, 5))
        motor_state["noise_floor"] = random.gauss(38, 2)
        motor_state["is_fault"] = True
    
    # Determine status
    motor_state["status"] = determine_status(
        motor_state["peak_freq"],
        motor_state["anomaly_score"]
    )


def generate_telemetry():
    """Generate telemetry packet to send to dashboard."""
    simulate_motor_behavior()
    
    spectrum = generate_frequency_spectrum(
        motor_state["peak_freq"],
        motor_state["anomaly_score"]
    )
    
    return {
        "peakFreq": round(motor_state["peak_freq"], 1),
        "frequencySpectrum": [round(x, 2) for x in spectrum],
        "anomalyScore": round(motor_state["anomaly_score"], 1),
        "status": motor_state["status"],
        "noiseFloor": round(motor_state["noise_floor"], 1),
        "timestamp": datetime.now().isoformat(),
        "motor_rpm": round(motor_state["rpm"], 0)
    }


async def handle_client(websocket):
    """
    Handle WebSocket client connection.
    Send telemetry updates every 500ms.
    """
    client_addr = websocket.remote_address
    print(f"✅ Client connected: {client_addr}")
    
    try:
        # Start telemetry stream
        while True:
            try:
                # Check for incoming messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                    handle_command(json.loads(message))
                except asyncio.TimeoutError:
                    pass
                
                # Generate and send telemetry
                telemetry = generate_telemetry()
                await websocket.send(json.dumps(telemetry))
                
                # Update interval: 500ms
                await asyncio.sleep(0.5)
            
            except websockets.exceptions.ConnectionClosed:
                break
    
    except Exception as e:
        print(f"❌ Error handling client {client_addr}: {e}")
    
    finally:
        print(f"🔌 Client disconnected: {client_addr}")


def handle_command(command):
    """Handle commands from the dashboard."""
    if command.get("command") == "calibrate":
        print(f"📊 Calibration request received (duration: {command.get('duration')}ms)")
        # In a real system, this would trigger noise floor sampling
        motor_state["noise_floor"] = 30.0
    
    elif command.get("command") == "alert":
        print(f"🚨 Alert trigger: {command.get('message')}")
        print(f"   Severity: {command.get('severity')}")
    
    elif command.get("command") == "reset":
        print("🔄 Reset command received")
        motor_state["time_started"] = datetime.now()


async def main():
    """Start WebSocket server."""
    print("=" * 60)
    print("🎯 Motor Bearing Fault Detection - WebSocket Test Server")
    print("=" * 60)
    print(f"📡 WebSocket server listening on ws://0.0.0.0:{WEBSOCKET_PORT}")
    print(f"🌐 Dashboard URL: http://localhost:8000")
    print(f"⏱️  Telemetry update interval: 500ms")
    print("\n📋 Simulation phases:")
    print("   0-60s:   Healthy operation (anomaly score: ~5%)")
    print("   60-120s: Early warning - friction detected (~20-50%)")
    print("   120-180s: Critical warning (~60-85%)")
    print("   180s+:   Critical fault (anomaly score: ~85-100%)")
    print("\n💡 Try opening multiple browser windows to connect multiple clients")
    print("💡 To test commands, send JSON from dashboard (calibrate, alert)")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 60)
    
    # Start WebSocket server
    async with websockets.serve(handle_client, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
