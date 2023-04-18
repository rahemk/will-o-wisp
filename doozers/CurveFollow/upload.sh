#!/bin/bash

../../bin/arduino-cli compile --fqbn pololu-a-star:avr:a-star32U4 CurveFollow.ino

../../bin/arduino-cli upload -p /dev/ttyACM0 --fqbn pololu-a-star:avr:a-star32U4 CurveFollow.ino
