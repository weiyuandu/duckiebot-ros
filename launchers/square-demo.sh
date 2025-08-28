#!/bin/bash

source /environment.sh

# initialize launch file
dt-launchfile-init

# Launch the mock LED emitter in background
rosrun my_package mock_led_emitter_node.py &
LED_PID=$!

# Wait for LED emitter to start
sleep 2

# Launch the light service in background  
rosrun my_package light_service_node.py &
LIGHT_PID=$!

# Wait for light service to start
sleep 2

# Launch the square controller
rosrun my_package square_controller_node.py &
SQUARE_PID=$!

# Wait for all processes
wait $LED_PID
wait $LIGHT_PID  
wait $SQUARE_PID

# wait for app to end
dt-launchfile-join
