#!/usr/bin/env python3

import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.srv import ChangePattern, ChangePatternResponse
from duckietown_msgs.msg import LEDPattern
from std_msgs.msg import String, ColorRGBA

class MockLEDEmitterNode(DTROS):
    """
    Mock LED emitter node for testing purposes.
    This simulates the LED emitter service that would be available on a real DuckieBot.
    """
    
    def __init__(self, node_name):
        super(MockLEDEmitterNode, self).__init__(
            node_name=node_name,
            node_type=NodeType.DRIVER
        )
        
        # LED protocol definitions (simplified version of real LED emitter)
        self._LED_protocol = {
            "colors": {
                "red": [1.0, 0.0, 0.0],
                "green": [0.0, 1.0, 0.0], 
                "blue": [0.0, 0.0, 1.0],
                "white": [1.0, 1.0, 1.0],
                "switchedoff": [0.0, 0.0, 0.0]
            },
            "signals": {
                "RED": {
                    "color_list": "red",
                    "frequency": 0,
                    "frequency_mask": [0, 0, 0, 0, 0]
                },
                "GREEN": {
                    "color_list": "green", 
                    "frequency": 0,
                    "frequency_mask": [0, 0, 0, 0, 0]
                },
                "BLUE": {
                    "color_list": "blue",
                    "frequency": 0,
                    "frequency_mask": [0, 0, 0, 0, 0]
                },
                "WHITE": {
                    "color_list": "white",
                    "frequency": 0,
                    "frequency_mask": [0, 0, 0, 0, 0]
                },
                "LIGHT_OFF": {
                    "color_list": "switchedoff",
                    "frequency": 0,
                    "frequency_mask": [0, 0, 0, 0, 0]
                }
            }
        }
        
        # Publisher for LED pattern (like real LED emitter)
        self._led_pub = rospy.Publisher(
            "~led_pattern", LEDPattern, queue_size=1
        )
        
        # Create the service that the light_service_node expects
        self._service = rospy.Service(
            "~set_pattern",
            ChangePattern,
            self._change_pattern_callback
        )
        
        self.log("Mock LED emitter node initialized and ready to receive color commands.")
        
    def _change_pattern_callback(self, req):
        """
        Handle LED pattern change requests
        """
        pattern_name = req.pattern_name.data.strip()
        self.log(f"🔴🟢🔵 Mock LED: Setting pattern to {pattern_name}")
        
        # Check if pattern exists
        if pattern_name not in self._LED_protocol["signals"]:
            self.logwarn(f"Unknown pattern: {pattern_name}")
            return ChangePatternResponse()
        
        # Get pattern definition
        pattern_def = self._LED_protocol["signals"][pattern_name]
        color_name = pattern_def["color_list"]
        
        # Get RGB values
        if color_name in self._LED_protocol["colors"]:
            rgb_color = self._LED_protocol["colors"][color_name]
        else:
            rgb_color = [0.0, 0.0, 0.0]  # Default to off
        
        # Create LED pattern message
        led_msg = LEDPattern()
        for i in range(5):  # DuckieBot has 5 LEDs
            rgba = ColorRGBA()
            rgba.r = rgb_color[0]
            rgba.g = rgb_color[1] 
            rgba.b = rgb_color[2]
            rgba.a = 1.0
            led_msg.rgb_vals.append(rgba)
        
        # Publish the LED pattern
        self._led_pub.publish(led_msg)
        
        # Visual feedback with emojis
        color_emojis = {
            "RED": "🔴",
            "GREEN": "🟢", 
            "BLUE": "🔵",
            "WHITE": "⚪",
            "LIGHT_OFF": "⚫"
        }
        
        emoji = color_emojis.get(pattern_name, "❓")
        print(f"\n{'='*50}")
        print(f"LED EMITTER: {emoji} {pattern_name} {emoji}")
        print(f"RGB: {rgb_color}")
        print(f"{'='*50}\n")
        
        return ChangePatternResponse()

if __name__ == '__main__':
    node = MockLEDEmitterNode(node_name='led_emitter_node')
    rospy.loginfo("Mock LED emitter service is running")
    rospy.spin()
