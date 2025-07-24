#include <Servo.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>

Servo thruster1, thruster2, thruster3, thruster4, thruster5, thruster6;

#define thruster1_pin 10
#define thruster2_pin 13
#define thruster3_pin 8
#define thruster4_pin 9
#define thruster5_pin 11
#define thruster6_pin 12

Adafruit_BNO055 bno = Adafruit_BNO055(55);

// Struct for AHRS data
struct IMUData {
  float roll;
  float pitch;
  float yaw;
} imuData;

void setup() {
  Serial.begin(115200);
  delay(1000);

  if (!bno.begin()) {
    while (1);  // Halt if BNO055 not found
  }

  bno.setExtCrystalUse(true);
  init_thruster();
  stop();
  delay(2000); // Stabilize ESCs
}

void loop() {
  // 1. Read and send AHRS data
  sensors_event_t orientationData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
  imuData.roll = orientationData.orientation.x;
  imuData.pitch = orientationData.orientation.y;
  imuData.yaw = orientationData.orientation.z;

  Serial.write((uint8_t*)&imuData, sizeof(imuData));  // Send 12 bytes

  // 2. Receive joystick data
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    int values[4];
    int index = 0;

    while (data.length() > 0 && index < 4) {
      int commaIndex = data.indexOf(',');
      String val = (commaIndex == -1) ? data : data.substring(0, commaIndex);
      if (commaIndex != -1) data = data.substring(commaIndex + 1); else data = "";
      values[index++] = val.toInt();
    }

    if (index == 4) {
      int lx = values[0], ly = values[1], rx = values[2], ry = values[3];

      if (abs(ry - 1500) > 50) {
        if (ry > 1500) downwards(ry, 3000 - ry);
        else upwards(ry, 3000 - ry);
      }
      else if (abs(ly - 1500) > 50) {
        if (ly < 1500) forward(ly);
        else backward(ly);
      }
      else if (abs(lx - 1500) > 50) {
        if (lx < 1500) left(lx, 3000 - lx);
        else right(lx, 3000 - lx);
      }
      else {
        stop();
      }
    }
  }

  delay(100); // 10 Hz update
}

void init_thruster() {
  thruster1.attach(thruster1_pin);
  thruster2.attach(thruster2_pin);
  thruster3.attach(thruster3_pin);
  thruster4.attach(thruster4_pin);
  thruster5.attach(thruster5_pin);
  thruster6.attach(thruster6_pin);
}

void forward(int us) {
  thruster1.writeMicroseconds(us);
  thruster2.writeMicroseconds(us);
  thruster5.writeMicroseconds(us);
  thruster6.writeMicroseconds(us);
}
void backward(int us) { forward(us); }
void upwards(int us, int us1) {
  thruster3.writeMicroseconds(us);
  thruster4.writeMicroseconds(us1);
}
void downwards(int us, int us1) { upwards(us, us1); }
void left(int us, int us1) {
  thruster1.writeMicroseconds(us);
  thruster2.writeMicroseconds(us1);
  thruster5.writeMicroseconds(us);
  thruster6.writeMicroseconds(us1);
}
void right(int us, int us1) { left(us, us1); }

void stop() {
  thruster1.writeMicroseconds(1500);
  thruster2.writeMicroseconds(1500);
  thruster3.writeMicroseconds(1500);
  thruster4.writeMicroseconds(1500);
  thruster5.writeMicroseconds(1500);
  thruster6.writeMicroseconds(1500);
}