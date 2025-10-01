// Example Arduino code for updating watering status on the Pi backend
// This shows how to control the watering system and update the status

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Pi backend details
const char* server_ip = "192.168.1.100";  // Your Pi's IP address
const int server_port = 8000;

// Pump control pin
const int PUMP_PIN = 4;

// Variables
bool watering_active = false;
unsigned long watering_start_time = 0;
int watering_duration = 30; // seconds

void setup() {
  Serial.begin(115200);
  
  // Initialize WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi connected!");
  
  // Initialize pump pin
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW); // Start with pump off
  
  Serial.println("Watering system initialized!");
}

void loop() {
  // Check if we need to stop watering
  if (watering_active && (millis() - watering_start_time) >= (watering_duration * 1000)) {
    stopWatering();
  }
  
  // Example: Start watering if humidity is too low
  if (!watering_active && shouldStartWatering()) {
    startWatering();
  }
  
  // Update watering status every 10 seconds
  static unsigned long last_status_update = 0;
  if (millis() - last_status_update >= 10000) {
    updateWateringStatus();
    last_status_update = millis();
  }
  
  delay(1000);
}

bool shouldStartWatering() {
  // Add your logic here to determine when to start watering
  // For example: check humidity sensor, soil moisture, etc.
  
  // Example: Start watering if humidity < 40%
  // float humidity = readHumiditySensor();
  // return humidity < 40.0;
  
  return false; // For now, don't auto-start
}

void startWatering() {
  Serial.println("Starting watering...");
  
  // Turn on pump
  digitalWrite(PUMP_PIN, HIGH);
  watering_active = true;
  watering_start_time = millis();
  
  // Update status on server
  updateWateringData(true, true); // pump_active=true, set last_watering
}

void stopWatering() {
  Serial.println("Stopping watering...");
  
  // Turn off pump
  digitalWrite(PUMP_PIN, LOW);
  watering_active = false;
  
  // Update status on server
  updateWateringData(false, false); // pump_active=false, don't update last_watering
}

void updateWateringStatus() {
  // Just update the current pump status without changing last_watering
  updateWateringData(watering_active, false);
}

void updateWateringData(bool pump_active, bool update_last_watering) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Construct URL
    String url = "http://" + String(server_ip) + ":" + String(server_port) + "/api/watering";
    
    // Create JSON payload
    StaticJsonDocument<200> doc;
    doc["pump_active"] = pump_active;
    doc["watering_duration"] = watering_duration;
    doc["auto_watering"] = true;
    doc["device_id"] = "autogrow_esp32";
    doc["timestamp"] = millis() / 1000; // Current timestamp in seconds
    
    // Only update last_watering timestamp when starting watering
    if (update_last_watering && pump_active) {
      // Convert current time to ISO format for last_watering
      time_t now = time(nullptr);
      char timeStr[25];
      strftime(timeStr, sizeof(timeStr), "%Y-%m-%dT%H:%M:%SZ", gmtime(&now));
      doc["last_watering"] = timeStr;
    }
    
    String jsonData;
    serializeJson(doc, jsonData);
    
    Serial.println("📦 Watering Update:");
    Serial.println(jsonData);
    
    // Send HTTP request
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.PUT(jsonData);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("✅ Watering Update Response: " + String(httpResponseCode));
      Serial.println("Response: " + response);
    } else {
      Serial.println("❌ HTTP Error: " + String(httpResponseCode));
    }
    
    http.end();
  } else {
    Serial.println("❌ WiFi not connected");
  }
}

// Manual watering function (call this from your main logic or via button press)
void manualWatering(int duration_seconds = 30) {
  if (!watering_active) {
    watering_duration = duration_seconds;
    startWatering();
  }
}

// Get current watering status from server
void getWateringStatus() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    String url = "http://" + String(server_ip) + ":" + String(server_port) + "/api/watering/autogrow_esp32";
    
    http.begin(url);
    int httpResponseCode = http.GET();
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Current watering status:");
      Serial.println(response);
      
      // Parse response to sync local state
      StaticJsonDocument<200> doc;
      deserializeJson(doc, response);
      
      bool server_pump_active = doc["pump_active"];
      if (server_pump_active != watering_active) {
        Serial.println("Syncing pump state with server...");
        if (server_pump_active) {
          digitalWrite(PUMP_PIN, HIGH);
          watering_active = true;
        } else {
          digitalWrite(PUMP_PIN, LOW);
          watering_active = false;
        }
      }
    } else {
      Serial.println("❌ Failed to get watering status: " + String(httpResponseCode));
    }
    
    http.end();
  }
}
