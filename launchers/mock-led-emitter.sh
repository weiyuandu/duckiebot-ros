#!/bin/bash

source /environment.sh

# initialize launch file
dt-launchfile-init

# launch the mock LED emitter node
rosrun my_package mock_led_emitter_node.py

# wait for app to end
dt-launchfile-join
