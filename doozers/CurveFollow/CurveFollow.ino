/*
Drives a Zumo32U4 robot to follow a white curve projected onto a surface.  The
assumption is that these are one of the Zumos equipped with a modified front
sensor array where the IR line tracking have been replaced with optical light
phototransistors.

Sensor reading 0 = white light
Sensor reading 2000 = black light
*/

#include <Wire.h>
#include <Zumo32U4.h>

// Motion-related constant which may need to be tuned.
const double TURN_FACTOR = 0.8;

// Maximum speed to apply to setSpeeds.  Nominally, this is 400 but we can
// decrease it to slow the robot down.
const int MAX_SPEED = 400;

const double MAX_SENSOR_VALUE = 2000;
const int NUM_SENSORS = 4;

// Global objects
Zumo32U4Motors motors;
Zumo32U4LineSensors lineSensors;
int lineSensorValues[NUM_SENSORS];

void setup()
{
    uint8_t pins[] = { SENSOR_DOWN1, SENSOR_DOWN2, SENSOR_DOWN4, SENSOR_DOWN5 };

    lineSensors.init(pins, 4);
}

void loop()
{
    // delay(10);

    lineSensors.read(lineSensorValues);

    // All four sensor values, normalized to [0, 1] where white = 1.
    double l = (MAX_SENSOR_VALUE - lineSensorValues[0]) / MAX_SENSOR_VALUE;
    double cl = (MAX_SENSOR_VALUE - lineSensorValues[1]) / MAX_SENSOR_VALUE;
    double cr = (MAX_SENSOR_VALUE - lineSensorValues[2]) / MAX_SENSOR_VALUE;
    double r = (MAX_SENSOR_VALUE - lineSensorValues[3]) / MAX_SENSOR_VALUE;

    double m = max(l, max(cl, max(cr, r)));
    if (m < 0.2) {
        motors.setSpeeds(0, 0);
        return;
    }

    // balance is effectively an error term which is zero when the amount of
    // light is perfectly balanced on either side; -1 when the light is on the
    // left; +1 when it is on the right.
    double balance = 0.5 * ((l + cl) - (cr + r));

    // These values are in the range [-1, 1].
    double leftSpeed = (1 - TURN_FACTOR) - TURN_FACTOR * balance;
    double rightSpeed = (1 - TURN_FACTOR) + TURN_FACTOR * balance;

    // Scale up to the maximum speed of the robot for each wheel.
    // setSpeeds expects values in the range [-400, 400].
    int16_t scaledLeftSpeed = (int16_t)(MAX_SPEED * leftSpeed);
    int16_t scaledRightSpeed = (int16_t)(MAX_SPEED * rightSpeed);

    motors.setSpeeds(scaledLeftSpeed, scaledRightSpeed);

    /*
    char buffer[250];
    sprintf(buffer, "line sensors: %4d %4d %4d %4d, balance: %f, raw speeds: %f %f, scaled speeds: %4d %4d\n",
        lineSensorValues[0],
        lineSensorValues[1],
        lineSensorValues[2],
        lineSensorValues[3],
        balance,
        leftSpeed,
        rightSpeed,
        scaledLeftSpeed,
        scaledRightSpeed);
    Serial.print(buffer);
    */
    Serial.print("LINE");
    Serial.print(l);
    Serial.print(", ");
    Serial.print(cl);
    Serial.print(", ");
    Serial.print(cr);
    Serial.print(", ");
    Serial.print(r);
    Serial.print(", ");
    Serial.print("\n");
    Serial.print("BAL");
    Serial.print(balance);
    Serial.print(", ");
    Serial.print("RAW");
    Serial.print(leftSpeed);
    Serial.print(", ");
    Serial.print(rightSpeed);
    Serial.print(", ");
    Serial.print("SCALED");
    Serial.print(scaledLeftSpeed);
    Serial.print(", ");
    Serial.print(scaledRightSpeed);
    Serial.print("\n");
}