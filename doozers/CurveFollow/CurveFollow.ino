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
const double TURN_FACTOR = 0.6;

// Maximum speed to apply to setSpeeds.  Nominally, this is 400 but we can
// decrease it to slow the robot down.
const int MAX_SPEED = 400;

const double MAX_SENSOR_VALUE = 2000;
const int NUM_SENSORS = 4;

// Global objects
Zumo32U4Motors motors;
Zumo32U4LineSensors lineSensors;
int lineSensorValues[NUM_SENSORS];

#define BUFFER_SIZE 10
int lBuffer[BUFFER_SIZE];
int clBuffer[BUFFER_SIZE];
int crBuffer[BUFFER_SIZE];
int rBuffer[BUFFER_SIZE];

void setup()
{
    uint8_t pins[] = { SENSOR_DOWN1, SENSOR_DOWN2, SENSOR_DOWN4, SENSOR_DOWN5 };

    lineSensors.init(pins, 4);
}

void loop()
{
//    delay(30);

    lineSensors.read(lineSensorValues);

    // Shift existing elements towards the head (erasing it).
    for (int i=1; i<BUFFER_SIZE; ++i) {
        lBuffer[i-1] = lBuffer[i];
        clBuffer[i-1] = clBuffer[i];
        crBuffer[i-1] = crBuffer[i];
        rBuffer[i-1] = rBuffer[i];
    }

    // Add the newest value at the tail.
    lBuffer[BUFFER_SIZE-1] = lineSensorValues[0];
    clBuffer[BUFFER_SIZE-1] = lineSensorValues[1];
    crBuffer[BUFFER_SIZE-1] = lineSensorValues[2];
    rBuffer[BUFFER_SIZE-1] = lineSensorValues[3];

    // Compute averages over each buffer
    double lAverage = 0;
    double clAverage = 0;
    double crAverage = 0;
    double rAverage = 0;
    for (int i = 0; i < BUFFER_SIZE; i++) {
        lAverage += lBuffer[i];
        clAverage += clBuffer[i];
        crAverage += crBuffer[i];
        rAverage += rBuffer[i];
    }
    lAverage /= BUFFER_SIZE;
    clAverage /= BUFFER_SIZE;
    crAverage /= BUFFER_SIZE;
    rAverage /= BUFFER_SIZE;

    /*
    Serial.print("AVERAGES. l, cl, cr, r: ");
    Serial.print(lAverage);
    Serial.print(" ");
    Serial.print(clAverage);
    Serial.print(" ");
    Serial.print(crAverage);
    Serial.print(" ");
    Serial.print(rAverage);
    Serial.print("\n");
    */

    // All four sensor values, normalized to [0, 1] where white = 1.
    //double l = (MAX_SENSOR_VALUE - lineSensorValues[0]) / MAX_SENSOR_VALUE;
    //double cl = (MAX_SENSOR_VALUE - lineSensorValues[1]) / MAX_SENSOR_VALUE;
    //double cr = (MAX_SENSOR_VALUE - lineSensorValues[2]) / MAX_SENSOR_VALUE;
    //double r = (MAX_SENSOR_VALUE - lineSensorValues[3]) / MAX_SENSOR_VALUE;
    double l = (MAX_SENSOR_VALUE - lAverage) / MAX_SENSOR_VALUE;
    double cl = (MAX_SENSOR_VALUE - clAverage) / MAX_SENSOR_VALUE;
    double cr = (MAX_SENSOR_VALUE - crAverage) / MAX_SENSOR_VALUE;
    double r = (MAX_SENSOR_VALUE - rAverage) / MAX_SENSOR_VALUE;

    double maximum = max(l, max(cl, max(cr, r)));
    if (maximum < 0.2) {
        motors.setSpeeds(0, 0);

        Serial.print("STOPPED. l, cl, cr, r: ");
        Serial.print(l);
        Serial.print(" ");
        Serial.print(cl);
        Serial.print(" ");
        Serial.print(cr);
        Serial.print(" ");
        Serial.print(r);
        Serial.print(", maximum: ");
        Serial.print(maximum);
        Serial.print("\n");
        return;
    }

    // balance is effectively an error term which is zero when the amount of
    // light is perfectly balanced on either side; -1 when the light is on the
    // left; +1 when it is on the right.
    double balance = 0.5 * (l + cl - cr - r);

    // These values are in the range [-1, 1].
    double rawLeftSpeed = (1 - TURN_FACTOR) - TURN_FACTOR * balance;
    double rawRightSpeed = (1 - TURN_FACTOR) + TURN_FACTOR * balance;

    // Scale up to the maximum speed of the robot for each wheel.
    // setSpeeds expects values in the range [-400, 400].
    int16_t scaledLeftSpeed = (int16_t)(MAX_SPEED * rawLeftSpeed);
    int16_t scaledRightSpeed = (int16_t)(MAX_SPEED * rawRightSpeed);

    motors.setSpeeds(scaledLeftSpeed, scaledRightSpeed);

    Serial.print("GO. l, cl, cr, r: ");
    Serial.print(l);
    Serial.print(" ");
    Serial.print(cl);
    Serial.print(" ");
    Serial.print(cr);
    Serial.print(" ");
    Serial.print(r);
    Serial.print(", balance: ");
    Serial.print(balance);
    Serial.print(", raw speeds: ");
    Serial.print(rawLeftSpeed);
    Serial.print("  ");
    Serial.print(rawRightSpeed);
    Serial.print(", scaled speeds: ");
    Serial.print(scaledLeftSpeed);
    Serial.print(" ");
    Serial.print(scaledRightSpeed);
    Serial.print("\n");
    */
}