#!/bin/bash

source /environment.sh

# initialize launch file
dt-launchfile-init

# launch the square controller node
rosrun my_package square_controller_node.py

# wait for app to end
dt-launchfile-join
