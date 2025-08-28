#!/bin/bash

source /environment.sh

# initialize launch file
dt-launchfile-init

# launch the light service node (which connects to real LED emitter)
dt-exec rosrun my_package light_service_node.py &

# wait for light service to initialize
sleep 2

# launch the square controller
dt-exec rosrun my_package square_controller_node.py

# wait for user
dt-launchfile-join
