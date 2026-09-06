#include <Arduino.h>
#include <WiFi.h>
// ===== FRONTEND INTEGRATION: required libraries =====
#include <WebSocketsServer.h>
#include <ArduinoJson.h>
// ===== END FRONTEND INTEGRATION =====
#include <driver/i2s.h>
#include <arduinoFFT.h>

const char* ssid = "PRAVEEN";
const char* password = "123456789";

#define I2S_WS 25
#define I2S_SD 32
#define I2S_SCK 33
#define I2S_PORT I2S_NUM_0
#define SAMPLES 512
#define SAMPLING_FREQ 16000.0
#define FRICTION_BIN_START 96
#define FRICTION_BIN_END 240
#define REQUIRED_ANOMALY_FRAMES 3

double vReal[SAMPLES];
double vImag[SAMPLES];
ArduinoFFT<double> FFT(vReal, vImag, SAMPLES, SAMPLING_FREQ);
// ===== FRONTEND INTEGRATION: WebSocket server =====
WebSocketsServer webSocket(8080);
// ===== END FRONTEND INTEGRATION =====

float ambientNoiseBaseline = 0.0;
float dynamicFrictionThreshold = 100.0;
bool isSystemCalibrated = false;
int anomalyConsecutiveCount = 0;

void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = (uint32_t)SAMPLING_FREQ,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 64,
    .use_apll = false
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };

  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
}

void captureLiveAudioSamples() {
  size_t bytes_read = 0;
  int32_t raw_sample = 0;

  for (int i = 0; i < SAMPLES; i++) {
    i2s_read(I2S_PORT, &raw_sample, sizeof(raw_sample), &bytes_read, portMAX_DELAY);
    vReal[i] = (double)(raw_sample >> 14);
    vImag[i] = 0.0;
  }
}

void computeFFT() {
  FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);
  FFT.compute(FFTDirection::Forward);
  FFT.complexToMagnitude();
}

double getFrictionBandEnergy() {
  double totalEnergy = 0.0;
  int numberOfBins = 0;

  for (int i = FRICTION_BIN_START; i <= FRICTION_BIN_END; i++) {
    totalEnergy += vReal[i] * vReal[i];
    numberOfBins++;
  }

  return numberOfBins > 0 ? totalEnergy / numberOfBins : 0.0;
}

void runAmbientNoiseCalibration() {
  Serial.println("\n==================================================");
  Serial.println("[M6: CALIBRATION STARTED] Sampling ambient room noise...");
  Serial.println(">> Ensure the test motor is OFF during these 3 seconds.");
  Serial.println("==================================================");

  float maxRoomNoiseObserved = 0.0;
  unsigned long calibrationStartTime = millis();

  while (millis() - calibrationStartTime < 3000) {
    captureLiveAudioSamples();
    computeFFT();

    float currentReading = (float)getFrictionBandEnergy();
    if (currentReading > maxRoomNoiseObserved) {
      maxRoomNoiseObserved = currentReading;
    }
    delay(10);
  }

  ambientNoiseBaseline = maxRoomNoiseObserved;
  dynamicFrictionThreshold = ambientNoiseBaseline * 1.30;

  if (dynamicFrictionThreshold < 80.0) {
    dynamicFrictionThreshold = 80.0;
  }

  isSystemCalibrated = true;
  anomalyConsecutiveCount = 0;

  Serial.println("[M6: CALIBRATION COMPLETE]");
  Serial.print(">> Baseline Room Noise      : ");
  Serial.println(ambientNoiseBaseline);
  Serial.print(">> Dynamic Friction Threshold: ");
  Serial.println(dynamicFrictionThreshold);
  Serial.println("==================================================\n");
}

bool evaluateMachineHealth(float liveFrictionEnergy) {
  return liveFrictionEnergy > dynamicFrictionThreshold;
}

// ===== FRONTEND INTEGRATION: send sensor data to script.js =====
void sendTelemetry(double dominantFreq, float frictionEnergy, bool criticalAnomaly) {
  float anomalyScore = 0.0;

  if (dynamicFrictionThreshold > 0.0 && frictionEnergy > dynamicFrictionThreshold) {
    anomalyScore = ((frictionEnergy - dynamicFrictionThreshold) /
                    dynamicFrictionThreshold) * 100.0;
    anomalyScore = constrain(anomalyScore, 0.0f, 100.0f);
  }

  const char* status = "HEALTHY";
  if (criticalAnomaly) {
    status = "CRITICAL";
  } else if (anomalyScore > 0.0) {
    status = "WARNING";
  }

  StaticJsonDocument<12000> telemetry;
  telemetry["peakFreq"] = dominantFreq;
  telemetry["anomalyScore"] = anomalyScore;
  telemetry["status"] = status;
  telemetry["noiseFloor"] = ambientNoiseBaseline;
  telemetry["sampleRate"] = (uint32_t)SAMPLING_FREQ;
  telemetry["fftSize"] = SAMPLES;

  JsonArray spectrum = telemetry.createNestedArray("frequencySpectrum");
  for (int i = 0; i < SAMPLES / 2; i++) {
    spectrum.add(constrain((float)vReal[i], 0.0f, 120.0f));
  }

  String payload;
  serializeJson(telemetry, payload);
  webSocket.broadcastTXT(payload);
}
// ===== END FRONTEND INTEGRATION =====
// ===== FRONTEND INTEGRATION: receive webpage commands =====
void handleWebSocketEvent(uint8_t client, WStype_t type, uint8_t* payload, size_t length) {
  if (type != WStype_TEXT) {
    return;
  }

  StaticJsonDocument<256> command;
  if (deserializeJson(command, payload, length)) {
    return;
  }

  const char* commandName = command["command"] | "";
  if (strcmp(commandName, "calibrate") == 0) {
    runAmbientNoiseCalibration();
  }
}
// ===== END FRONTEND INTEGRATION =====

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\nInitializing Acoustic Machine Health Monitor...");

  Serial.print("Connecting to Wi-Fi");
  WiFi.begin(ssid, password);
  unsigned long wifiStart = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - wifiStart < 20000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi Connected!");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWi-Fi connection failed; no IP address was assigned.");
    Serial.print("Wi-Fi status code: ");
    Serial.println(WiFi.status());
  }

  // Original team hardware initialization
  setupI2S();
  Serial.println("I2S Microphone Initialized.");

  runAmbientNoiseCalibration();

  // ===== FRONTEND INTEGRATION: start WebSocket server =====
  if (WiFi.status() == WL_CONNECTED) {
    webSocket.begin();
    webSocket.onEvent(handleWebSocketEvent);
  }
  // ===== END FRONTEND INTEGRATION =====

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WebSocket server started on port 8080.");
  } else {
    Serial.println("WebSocket server not started because Wi-Fi is unavailable.");
  }
  Serial.println("Ready. Type 'c' in Serial Monitor anytime to re-calibrate.\n");
}

void loop() {
  // ===== FRONTEND INTEGRATION: keep WebSocket active =====
  webSocket.loop();
  // ===== END FRONTEND INTEGRATION =====

  if (Serial.available() > 0) {
    char ch = Serial.read();
    if (ch == 'c' || ch == 'C') {
      runAmbientNoiseCalibration();
    }
  }

  captureLiveAudioSamples();
  computeFFT();

  double dominantFreq = FFT.majorPeak();
  float frictionEnergy = (float)getFrictionBandEnergy();
  bool singleFrameAnomaly = evaluateMachineHealth(frictionEnergy);

  if (singleFrameAnomaly) {
    anomalyConsecutiveCount++;
  } else {
    anomalyConsecutiveCount = 0;
  }

  bool criticalAnomaly = anomalyConsecutiveCount >= REQUIRED_ANOMALY_FRAMES;

  Serial.print("Dom Freq: ");
  Serial.print(dominantFreq, 1);
  Serial.print(" Hz | Friction Energy: ");
  Serial.print(frictionEnergy, 1);
  Serial.print(" | Thresh: ");
  Serial.print(dynamicFrictionThreshold, 1);

  if (criticalAnomaly) {
    Serial.println(" >>> [CRITICAL ANOMALY DETECTED!] <<<");
  } else {
    Serial.println(" | [STATUS: HEALTHY]");
  }

  // ===== FRONTEND INTEGRATION: send current FFT result =====
  sendTelemetry(dominantFreq, frictionEnergy, criticalAnomaly);
  // ===== END FRONTEND INTEGRATION =====
  delay(100);
}