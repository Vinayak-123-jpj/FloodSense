/*
 * =====================================================================================
 *  FloodSense ESP32 Autonomous Monitoring Station Firmware
 * =====================================================================================
 *  PLANNED HARDWARE BLUEPRINT — NOT BUILT IN THIS ROUND (SOFTWARE SIMULATION ONLY)
 * 
 *  Target Microcontroller: ESP32-WROOM-32 (NodeMCU / DevKit V1)
 *  Sensors: 
 *    1. JSN-SR04T Waterproof Ultrasonic Sensor (Water Level Distance)
 *    2. Tipping Bucket Rain Gauge Reed Switch (Interrupt Count)
 *    3. Battery Voltage Divider ADC (Pin 34)
 * 
 *  Communication Protocol: HTTP POST / JSON payload over Wi-Fi / 4G Modem
 *  Power Source: 6V 5W Solar Panel + 18650 LiFePO4 / Li-Ion Battery Stack + TP4056 / CN3791
 * =====================================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Wi-Fi Access Point Credentials
const char* WIFI_SSID = "FloodSense_Node_Net";
const char* WIFI_PASS = "EmergencyAccess2026";

// FloodSense Central Ingestion Server URL
const char* API_SERVER_URL = "http://floodsense.local/api/readings";

// Station Hardware Identification
const char* NODE_ID = "KL-PER-01";
const float SENSOR_MOUNT_HEIGHT_CM = 800.0; // Sensor distance from riverbed in cm

// Pin Definitions
#define TRIG_PIN 5
#define ECHO_PIN 18
#define RAIN_INTERRUPT_PIN 19
#define BATTERY_ADC_PIN 34

// Global Variables
volatile unsigned long rain_pulse_count = 0;
unsigned long last_reading_time = 0;
const unsigned long SAMPLING_INTERVAL_MS = 10000; // Send telemetry every 10 seconds

// ISR for Tipping Bucket Rain Gauge (0.2794mm per tip)
void IRAM_ATTR rainBucketTipped() {
    rain_pulse_count++;
}

float measureWaterLevelCm() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration_us = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms timeout
    if (duration_us == 0) {
        return -1.0; // Distance measurement timeout/error
    }

    float distance_cm = (duration_us * 0.0343) / 2.0;
    // Water level height = Mount height - distance to surface
    float water_level_cm = SENSOR_MOUNT_HEIGHT_CM - distance_cm;
    return (water_level_cm > 0) ? water_level_cm : 0.0;
}

float measureBatteryPct() {
    int raw_adc = analogRead(BATTERY_ADC_PIN);
    float voltage = (raw_adc / 4095.0) * 3.3 * 2.0; // 1:1 voltage divider
    float pct = ((voltage - 3.2) / (4.2 - 3.2)) * 100.0;
    return constrain(pct, 0.0, 100.0);
}

void setup() {
    Serial.begin(115200);
    Serial.println("[FloodSense Node] Initializing ESP32 hardware peripherals...");

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(RAIN_INTERRUPT_PIN, INPUT_PULLUP);

    attachInterrupt(digitalPinToInterrupt(RAIN_INTERRUPT_PIN), rainBucketTipped, FALLING);

    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("[Wi-Fi] Connecting");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n[Wi-Fi] Connected! IP: " + WiFi.localIP().toString());
}

void loop() {
    if (millis() - last_reading_time >= SAMPLING_INTERVAL_MS) {
        last_reading_time = millis();

        if (WiFi.status() == WL_CONNECTED) {
            float water_level_cm = measureWaterLevelCm();
            
            // Calculate mm/hr from pulse count
            float rainfall_mm_hr = (rain_pulse_count * 0.2794) * (3600.0 / (SAMPLING_INTERVAL_MS / 1000.0));
            rain_pulse_count = 0; // Reset counter for next window

            float battery_pct = measureBatteryPct();
            int rssi = WiFi.RSSI();

            // Construct JSON document
            StaticJsonDocument<256> doc;
            doc["node_id"] = NODE_ID;
            doc["water_level_cm"] = water_level_cm;
            doc["rainfall_mm_hr"] = rainfall_mm_hr;
            doc["battery_pct"] = battery_pct;
            doc["rssi"] = rssi;

            String requestBody;
            serializeJson(doc, requestBody);

            HTTPClient http;
            http.begin(API_SERVER_URL);
            http.addHeader("Content-Type", "application/json");

            int httpCode = http.POST(requestBody);
            Serial.printf("[HTTP] POST Result Code: %d\n", httpCode);
            http.end();
        }
    }
}
