#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// -------- WiFi --------
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// -------- MQTT --------
const char* mqttServer = "broker.hivemq.com";
const int mqttPort = 1883;

// MQTT Topics
const char* tempTopic = "iot/plant1/temperature";
const char* soilTopic = "iot/plant1/soil";

// -------- Sensors --------
#define DHTPIN 21
#define DHTTYPE DHT22
#define SOIL_PIN 34

DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient client(espClient);

// -------- Functions --------
void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
}

void connectToMQTT() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32_Plant_Monitor")) {
      Serial.println("Connected!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  connectToWiFi();

  client.setServer(mqttServer, mqttPort);
  connectToMQTT();
}

void loop() {
  if (!client.connected()) {
    connectToMQTT();
  }
  client.loop();

  float temperature = dht.readTemperature();
  int soilValue = analogRead(SOIL_PIN);

  if (!isnan(temperature)) {
    char tempStr[8];
    dtostrf(temperature, 1, 2, tempStr);
    client.publish(tempTopic, tempStr);
  }

  char soilStr[8];
  itoa(soilValue, soilStr, 10);
  client.publish(soilTopic, soilStr);

  Serial.println("Data sent to MQTT");
  delay(5000); // Send every 5 seconds
}