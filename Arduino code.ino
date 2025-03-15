#define BLYNK_PRINT Serial
#define BLYNK_TEMPLATE_ID "TMPL3xRODO13E"
#define BLYNK_TEMPLATE_NAME "Synus"
#define BLYNK_AUTH_TOKEN "V0L_6yQd_MLwIFHhfyqaFPDe78fxPRMe"

#include <WiFi.h>
#include <Wire.h>
#include <HTTPClient.h>
#include <Adafruit_MLX90614.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP085.h>
#include <DHT.h>
#include <BlynkSimpleEsp32.h>
#include <ThingSpeak.h>

Adafruit_BMP085 bmp;
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
WiFiClient client;

// Wi-Fi Credentials
const char* ssid = "Act";
const char* password = "Madhumakeskilled";

// ThingSpeak API
int channelID = 2225368; // Replace with your ThingSpeak Channel ID
const char* apiKey = "VUX286JN0ZVGAPGQ";
const char* server = "api.thingspeak.com";

int outputChannelID = 2225369; // Replace with your output ThingSpeak Channel ID (Public)

// Blynk Authentication Token
char auth[] = BLYNK_AUTH_TOKEN;

// Define Pin Constants
#define DHTPIN 4         
#define DHTTYPE DHT11    
#define RELAY_PIN 5      
#define MQ135_PIN 34     
#define RELAY2_PIN 18  // Second Relay controlled via Field 8

DHT dht(DHTPIN, DHTTYPE);

#define TEMP_THRESHOLD 30.0  

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to Wi-Fi");

    Blynk.begin(auth, ssid, password);
    ThingSpeak.begin(client);

    if (!mlx.begin()) {
        Serial.println("Error connecting to MLX90614 sensor. Check wiring!");
        while (1);
    }

    if (!bmp.begin()) {
        Serial.println("Could not find a valid BMP085 sensor, check wiring!");
        while (1);
    }

    dht.begin();

    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, HIGH); 

    pinMode(RELAY2_PIN, OUTPUT);
    digitalWrite(RELAY2_PIN, HIGH);
}

void loop() {
    float dht_temp = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (isnan(dht_temp) || isnan(humidity)) {
        Serial.println("Failed to read from DHT sensor!");
        return;
    }

    Serial.print("Temperature = ");
    Serial.print(dht_temp);
    Serial.println(" *C");

    float temp = bmp.readTemperature();
    float pres = bmp.readPressure();

    Serial.print("Pressure = ");
    Serial.print(pres);
    Serial.println(" Pa");

    float mlx_temp = mlx.readObjectTempC();
    Serial.print("Ambient Temperature: ");
    Serial.print(mlx_temp);
    Serial.println(" *C");

    int mq135_value = analogRead(MQ135_PIN);
    Serial.println(mq135_value);

    bool fan_status = false;
    if ((dht_temp + mlx_temp) / 2 > TEMP_THRESHOLD || humidity > 70) {
        digitalWrite(RELAY_PIN, LOW);  
        fan_status = true;
        Serial.println("🔥 High Temp/Humidity! Cooling Fan Activated.");
    } else {
        digitalWrite(RELAY_PIN, HIGH);  
        fan_status = false;
        Serial.println("✅ Temperature Normal. Fan OFF.");
    }

    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String url = String("http://") + server + "/update?api_key=" + apiKey +
                     "&field1=" + String(dht_temp) +
                     "&field2=" + String(humidity) +
                     "&field3=" + String(mlx_temp) +
                     "&field4=" + String(pres) +
                     "&field5=" + String(temp) +
                     "&field6=" + String(mq135_value) +
                     "&field7=" + String(fan_status);

        http.begin(url);
        int httpResponseCode = http.GET();
        if (httpResponseCode > 0) {
            Serial.println("✅ Data Sent to ThingSpeak");
        } else {
            Serial.print("❌ Error Sending Data: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    }

    if (mq135_value > 1000) {
        Blynk.logEvent("gas_warning", "Gas level exceeds threshold!");
        Serial.println("⚠️ Gas level exceeded 1000! Logging event to Blynk.");
    }

    if ((dht_temp + mlx_temp) / 2 > TEMP_THRESHOLD) {
        Blynk.logEvent("high_temp_warning", "High temperature detected!");
        Serial.println("⚠️ High Temperature Detected! Logging event to Blynk.");
    }

    if (humidity > 70) {
        Blynk.logEvent("high_humidity_warning", "High humidity detected!");
        Serial.println("⚠️ High Humidity Detected! Logging event to Blynk.");
    }

    Blynk.virtualWrite(V1, dht_temp);
    Blynk.virtualWrite(V2, humidity);
    Blynk.virtualWrite(V3, mlx_temp);
    Blynk.virtualWrite(V4, pres);
    Blynk.virtualWrite(V5, mq135_value);

    int status = 0;  
    int motor = ThingSpeak.readIntField(outputChannelID, 1); 

    if (motor == 1) {
        Serial.println("✅ Field Read 1! Turning ON Relay 2.");
        digitalWrite(RELAY2_PIN, LOW);  // Turn ON relay
    } else {
        Serial.print("❌ Received 2 ");
        Serial.println(status);
        digitalWrite(RELAY2_PIN, HIGH);  // Turn OFF relay
    }

    Blynk.run();
    delay(1000);
}
