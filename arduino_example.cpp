// Example Arduino code for sending sensor data to the Pi backend
// Updated to use the new JSON payload structure

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Pi backend details
const char* server_ip = "192.168.1.100";  // Your Pi's IP address
const int server_port = 8000;
const String device_id = "autogrow_esp32";
const String firmware_version = "1.0.0";
const String sensor_type = "DHT11_LDR";

// Sensor pins
const int DHT_PIN = 2;
const int LDR_PIN = A0;
const int PUMP_PIN = 4;

// Variables
float temperature = 0.0;
float humidity = 0.0;
int lux = 0;
bool pumpActive = false;

void setup() {
  Serial.begin(115200);
  
  // Initialize WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi connected!");
  
  // Initialize pins
  pinMode(PUMP_PIN, OUTPUT);
  
  Serial.println("Setup complete!");
}

void loop() {
  // Read sensors
  readSensors();
  
  // Send data to Pi backend
  sendSensorData();
  
  // Wait 30 seconds before next reading
  delay(30000);
}

void readSensors() {
  // Read DHT11 sensor (temperature and humidity)
  // Note: You'll need to implement DHT11 reading based on your library
  temperature = 25.5;  // Example value
  humidity = 60.2;     // Example value
  
  // Read LDR sensor (light level)
  int rawValue = analogRead(LDR_PIN);
  lux = map(rawValue, 0, 1023, 0, 1000);  // Convert to lux
  
  // Read pump status
  pumpActive = digitalRead(PUMP_PIN) == HIGH;
  
  Serial.println("Sensor readings:");
  Serial.println("Temperature: " + String(temperature) + "°C");
  Serial.println("Humidity: " + String(humidity) + "%");
  Serial.println("Light: " + String(lux) + " lux");
  Serial.println("Pump: " + String(pumpActive ? "Active" : "Inactive"));
}

void sendSensorData() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Construct URL
    String url = "http://" + String(server_ip) + ":" + String(server_port) + "/api/v1/sensor-data";
    
    // Create JSON payload
    StaticJsonDocument<200> doc;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["lux"] = lux;
    doc["pumpActive"] = pumpActive;
    doc["timestamp"] = millis();  // Use millis() or get actual timestamp
    doc["device_id"] = device_id;
    doc["firmware_version"] = firmware_version;
    doc["sensor_type"] = sensor_type;
    
    String jsonData;
    serializeJson(doc, jsonData);
    
    Serial.println("📦 JSON Data:");
    Serial.println(jsonData);
    
    // Send HTTP request
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(jsonData);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("✅ HTTP Response: " + String(httpResponseCode));
      Serial.println("Response: " + response);
    } else {
      Serial.println("❌ HTTP Error: " + String(httpResponseCode));
    }
    
    http.end();
  } else {
    Serial.println("❌ WiFi not connected");
  }
}
