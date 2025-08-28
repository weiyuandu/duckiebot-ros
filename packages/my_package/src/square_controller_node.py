#!/usr/bin/env python3

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.srv import ChangePattern, ChangePatternRequest
from std_msgs.msg import String
import time
import numpy as np

class SquareControllerNode(DTROS):
    """
    Open-loop square controller that moves the duckiebot in a 1m x 1m square
    with different LED colors at each corner. Connects directly to real LED emitter only.
    """
    
    def __init__(self, node_name):
        super(SquareControllerNode, self).__init__(
            node_name=node_name,
            node_type=NodeType.CONTROL
        )
        
        # Get vehicle name from namespace (like in the reference code)
        self.veh_name = rospy.get_namespace().strip("/")
        
        # If no vehicle name from namespace, use environment variable as fallback
        if not self.veh_name:
            self.veh_name = os.environ.get('VEHICLE_NAME', 'duck')
        
        # Publisher for movement commands - using the car command switch node topic
        car_cmd_topic = f"/{self.veh_name}/car_cmd_switch_node/cmd"
        self._car_cmd_publisher = rospy.Publisher(
            car_cmd_topic, 
            Twist2DStamped, 
            queue_size=1
        )
        
        # Service client for LED control - connect directly to real LED emitter only
        led_service_name = f"/{self.veh_name}/led_emitter_node/set_pattern"
        try:
            rospy.wait_for_service(led_service_name, timeout=5.0)
            self._led_service = rospy.ServiceProxy(led_service_name, ChangePattern)
            self._led_available = True
            self.log(f"Connected to real LED emitter: {led_service_name}")
        except rospy.ROSException:
            self.logwarn(f"Real LED emitter service not available at {led_service_name}. Will continue without LED control.")
            self._led_service = None
            self._led_available = False
        
        # Movement parameters (calibrated for real Duckiebot)
        self._linear_velocity = 0.4   # m/s - good speed for real bot
        self._angular_velocity = 2.0  # rad/s - good turning speed
        self._edge_distance = 1.0     # meters
        
        # Calculate timing for 1-meter movement and 90-degree turn
        self._move_time = self._edge_distance / self._linear_velocity  # time to move 1 meter
        self._turn_time = (np.pi / 2) / self._angular_velocity         # time for 90-degree turn
        
        # Colors for each corner of the square (using real LED emitter protocol patterns)
        self._corner_colors = ["RED", "GREEN", "BLUE", "WHITE"]
        
        # Available LED patterns (from real LED emitter protocol)
        self._available_patterns = ["RED", "GREEN", "WHITE", "BLUE", "LIGHT_OFF", "CAR_DRIVING", "CAR_SIGNAL_A"]
        
        self.log(f"Square controller initialized. Move time: {self._move_time:.2f}s, Turn time: {self._turn_time:.2f}s")
        self.log(f"Vehicle name: {self.veh_name}")
        self.log(f"Publishing movement commands to: {car_cmd_topic}")

    def set_led_color(self, color):
        """Set the LED color using the real LED emitter service"""
        if not self._led_available:
            self.log(f"LED service not available, would set color to {color}")
            return
            
        # Validate color pattern is available
        if color not in self._available_patterns:
            self.logwarn(f"Pattern '{color}' not in available patterns {self._available_patterns}")
            return
            
        try:
            # Create the correct request object with String message (as per LED emitter service definition)
            request = ChangePatternRequest()
            request.pattern_name = String(data=color)
            response = self._led_service(request)
            self.log(f"🎨 LED pattern changed to {color}")
        except rospy.ServiceException as e:
            self.logwarn(f"Failed to change LED pattern: {e}")

    def publish_car_cmd(self, linear_v, angular_v):
        """Publish a car command (adapted from EncoderPoseNode)"""
        car_control_msg = Twist2DStamped()
        car_control_msg.header.stamp = rospy.Time.now()
        car_control_msg.v = linear_v      # linear velocity
        car_control_msg.omega = angular_v # angular velocity
        self._car_cmd_publisher.publish(car_control_msg)
        
        # Debug output to confirm commands are being sent
        if linear_v != 0 or angular_v != 0:
            self.log(f"🚗 Sending cmd: v={linear_v:.2f}, ω={angular_v:.2f}")

    def stop_robot(self):
        """Stop the robot"""
        self.publish_car_cmd(0.0, 0.0)

    def move_forward(self, duration):
        """Move forward for specified duration"""
        self.log(f"Moving forward for {duration:.2f} seconds")
        rate = rospy.Rate(10)  # 10 Hz
        end_time = rospy.Time.now() + rospy.Duration(duration)
        
        while rospy.Time.now() < end_time and not rospy.is_shutdown():
            self.publish_car_cmd(self._linear_velocity, 0.0)
            rate.sleep()
        
        self.stop_robot()

    def turn_left(self, duration):
        """Turn left (counterclockwise) for specified duration"""
        self.log(f"Turning left for {duration:.2f} seconds")
        rate = rospy.Rate(10)  # 10 Hz
        end_time = rospy.Time.now() + rospy.Duration(duration)
        
        while rospy.Time.now() < end_time and not rospy.is_shutdown():
            self.publish_car_cmd(0.0, self._angular_velocity)
            rate.sleep()
        
        self.stop_robot()

    def execute_square(self):
        """Execute one complete square movement"""
        self.log("Starting square movement...")
        
        for corner in range(4):
            if rospy.is_shutdown():
                break
                
            # Set LED color for this corner
            color = self._corner_colors[corner]
            self.set_led_color(color)
            self.log(f"Corner {corner + 1}: LED set to {color}")
            
            # Small pause to see the color change
            rospy.sleep(1.0)
            
            # Move forward along the edge
            self.move_forward(self._move_time)
            
            # Small pause between movement and turn
            rospy.sleep(0.5)
            
            # Turn left 90 degrees (except after the last edge)
            if corner < 3:  # Don't turn after the 4th edge
                self.turn_left(self._turn_time)
                rospy.sleep(0.5)
        
        # Turn off LEDs when done
        self.set_led_color("LIGHT_OFF")
        self.log("Square movement completed!")

    def run(self):
        """Main run loop"""
        # Wait a bit for everything to initialize
        rospy.sleep(2.0)
        
        # Execute the square movement
        self.execute_square()
        
        # Keep node alive for a bit
        rospy.sleep(2.0)

    def on_shutdown(self):
        """Cleanup when shutting down"""
        self.stop_robot()
        if self._led_available:
            self.set_led_color("LIGHT_OFF")
        self.log("Square controller shutting down...")

if __name__ == '__main__':
    node = SquareControllerNode(node_name='square_controller_node')
    
    # Register shutdown hook
    rospy.on_shutdown(node.on_shutdown)
    
    try:
        node.run()
    except rospy.ROSInterruptException:
        pass
    
    rospy.spin()
