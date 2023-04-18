This folder contains the Arduino sketch to drive a Zumo32U4 robot to follow a
white curve projected onto a surface.  The assumption is that these are one of
the Zumos equipped with a modified front sensor array where the IR line tracking
have been replaced with optical light phototransistors.

Execute the following command to compile and upload the sketch to the Zumo:

    ./upload.sh

Once the sketch is uploaded to the Zumo, you can interact directly with it
over the serial monitor by executing the following

    ./monitor.sh

------------------------------------------------------------------------
18 April, 2023
Andrew Vardy
