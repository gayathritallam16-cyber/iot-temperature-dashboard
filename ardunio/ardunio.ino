#include <ESP8266WiFi.h>
#include <DHT.h>
#include <PubSubClient.h>

// -------------------------
// SENSOR PINS
// -------------------------

#define DHTPIN D2
#define DHTTYPE DHT11
#define RELAY D1

// -------------------------
// WIFI
// -------------------------

const char* ssid = "Sumalatha";
const char* password = "123456789";

// -------------------------
// MQTT
// -------------------------

// IMPORTANT:
// Change this to the IP address of your MQTT broker
const char* mqtt_server = "10.52.179.37";

const int mqtt_port = 1883;

const char* mqtt_topic = "iot/temperature";

const char* mqtt_client_id = "ESP8266_DHT11";

// -------------------------

DHT dht(DHTPIN, DHTTYPE);

WiFiClient espClient;
PubSubClient mqttClient(espClient);

unsigned long lastPublish = 0;


// -------------------------
// WIFI CONNECTION
// -------------------------

void setup_wifi() {

  delay(10);

  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);

    Serial.print(".");
  }

  Serial.println();

  Serial.println("WiFi Connected!");

  Serial.print("ESP8266 IP Address: ");

  Serial.println(WiFi.localIP());
}


// -------------------------
// MQTT CONNECTION
// -------------------------

void reconnectMQTT() {

  while (!mqttClient.connected()) {

    Serial.print("Connecting to MQTT...");

    if (mqttClient.connect(mqtt_client_id)) {

      Serial.println("CONNECTED!");

    }

    else {

      Serial.print("FAILED, rc=");

      Serial.print(mqttClient.state());

      Serial.println(" retrying in 5 seconds");

      delay(5000);
    }
  }
}


// -------------------------
// SETUP
// -------------------------

void setup() {

  Serial.begin(9600);

  dht.begin();

  pinMode(RELAY, OUTPUT);

  digitalWrite(RELAY, LOW);

  // WiFi
  setup_wifi();

  // MQTT
  mqttClient.setServer(
    mqtt_server,
    mqtt_port
  );

  Serial.println("MQTT configured");
}


// -------------------------
// LOOP
// -------------------------

void loop() {

  // Make sure MQTT is connected

  if (!mqttClient.connected()) {

    reconnectMQTT();
  }

  mqttClient.loop();


  // Publish every 2 seconds

  if (millis() - lastPublish >= 2000) {

    lastPublish = millis();

    // Read temperature

    float temperature =
      dht.readTemperature();


    if (isnan(temperature)) {

      Serial.println(
        "Failed to read DHT11!"
      );

      return;
    }


    // Relay control

    String relayStatus;


    if (temperature > 33) {

      digitalWrite(RELAY, HIGH);

      relayStatus = "ON";

      Serial.println(
        "Temperature > 33°C -> RELAY ON"
      );

    }

    else {

      digitalWrite(RELAY, LOW);

      relayStatus = "OFF";

      Serial.println(
        "Temperature <= 30°C -> RELAY OFF"
      );
    }


    // -------------------------
    // CREATE JSON
    // -------------------------

    String payload = "{";

    payload += "\"temperature\":";
    payload += String(temperature, 2);

    payload += ",";

    payload += "\"relay\":\"";
    payload += relayStatus;
    payload += "\"";

    payload += "}";


    // -------------------------
    // MQTT PUBLISH
    // -------------------------

    bool success =
      mqttClient.publish(
        mqtt_topic,
        payload.c_str()
      );


    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");

    Serial.print("Relay: ");
    Serial.println(relayStatus);

    Serial.print("MQTT Payload: ");
    Serial.println(payload);


    if (success) {

      Serial.println(
        "MQTT Published Successfully"
      );

    }

    else {

      Serial.println(
        "MQTT Publish Failed"
      );
    }

    Serial.println("--------------------");
  }
}