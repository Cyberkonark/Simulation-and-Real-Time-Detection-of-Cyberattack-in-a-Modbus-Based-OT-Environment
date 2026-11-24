
#include <OneWire.h>
#include <DallasTemperature.h>

// Water-level sensor
const int waterSensor = A1;

// DS18B20 temperature sensor
#define ONE_WIRE_BUS 2

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Blue LED
const int blueLED = 8;

// Water-level calibration
// Update these after measuring your dry and full readings.
const int DRY_VALUE = 220;
const int FULL_VALUE = 640;

void setup() {
  Serial.begin(9600);

  pinMode(blueLED, OUTPUT);
  digitalWrite(blueLED, LOW);

  sensors.begin();
}

void loop() {

  // Read water-level sensor (average 10 readings)
  long total = 0;

  for (int i = 0; i < 10; i++) {
    total += analogRead(waterSensor);
    delay(20);
  }

  int rawValue = total / 10;

  // Convert sensor reading to estimated percentage
  int waterLevel = map(
    rawValue,
    DRY_VALUE,
    FULL_VALUE,
    0,
    100
  );

  waterLevel = constrain(waterLevel, 0, 100);

  // Read temperature
  sensors.requestTemperatures();

  float temperature = sensors.getTempCByIndex(0);

  // Check sensor readings
  bool validTemperature =
    temperature != DEVICE_DISCONNECTED_C &&
    temperature >= -55 &&
    temperature <= 125;

  bool validWater =
    rawValue >= 0 && rawValue <= 1023;

  // Blue LED indicates valid sensor readings
  if (validTemperature && validWater) {
    digitalWrite(blueLED, HIGH);
  } else {
    digitalWrite(blueLED, LOW);
  }

  // Send data to Serial Monitor
  if (validTemperature && validWater) {

    Serial.print("Water Level: ");
    Serial.print(waterLevel);

    Serial.print("% | Temperature: ");
    Serial.println(temperature);

  } else {
    Serial.println("Sensor Error!");
  }

  delay(1000);
}
