#!/bin/bash

source /environment.sh

# initialize launch file
dt-launchfile-init

# start roscore in background if not already running
dt-exec roscore &
ROSCORE_PID=$!

# wait for roscore to start
sleep 5

# launch the real LED emitter (in case it's not already running)
dt-exec rosrun my_package led_emitter_node.py &
LED_PID=$!

# wait for LED emitter to initialize
sleep 3

# launch the square controller (which connects directly to real LED emitter)
dt-exec rosrun my_package square_controller_node.py &
SQUARE_PID=$!

# wait for all processes
wait $ROSCORE_PID
wait $LED_PID
wait $SQUARE_PID

# wait for user
dt-launchfile-join
