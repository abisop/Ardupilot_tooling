#!/usr/bin/env python3

"""ROS2 node that publishes coordinates to a topic.

This script publishes car positions as PointStamped messages to a ROS2 topic
at a configurable publish rate. It can be used by a trajectory follower or
visualization node.
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped


class CarPositionPublisher(Node):
    def __init__(self):
        super().__init__('car_position_publisher')

        self.declare_parameter('topic_name', '/car/position')
        self.declare_parameter('frame_id', 'map')
        self.declare_parameter('publish_rate_hz', 50)
        self.declare_parameter('radius', 10)
        self.declare_parameter('target_velocity_mps', 2)
        self.declare_parameter('loop', True)

        self.topic_name = self.get_parameter('topic_name').value
        self.frame_id = self.get_parameter('frame_id').value
        self.publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        self.radius = float(self.get_parameter('radius').value)
        self.target_velocity_mps = float(self.get_parameter('target_velocity_mps').value)
        self.loop = bool(self.get_parameter('loop').value)

        self.publisher = self.create_publisher(PointStamped, self.topic_name, 10)
        self.current_angle_rad = 0.0
        self.timer = self.create_timer(1.0 / self.publish_rate_hz, self.publish_next_position)

        self.get_logger().info(
            f'CarPositionPublisher started: topic={self.topic_name}, '
            f'rate={self.publish_rate_hz}Hz, velocity={self.target_velocity_mps}m/s, radius={self.radius}m, loop={self.loop}'
        )

    def publish_next_position(self):
        msg = PointStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id

        angular_speed_rad_per_s = self.target_velocity_mps / self.radius
        delta_angle_rad = angular_speed_rad_per_s / self.publish_rate_hz

        self.current_angle_rad += delta_angle_rad

        if self.loop:
            self.current_angle_rad = math.fmod(self.current_angle_rad, 2.0 * math.pi)
            if self.current_angle_rad < 0:
                self.current_angle_rad += 2.0 * math.pi
        else:
            if self.current_angle_rad > 2.0 * math.pi:
                self.get_logger().info('Completed one circle. Shutting down.')
                self.timer.cancel()
                self.destroy_node()
                rclpy.shutdown()
                return

        msg.point.x = self.radius * math.cos(self.current_angle_rad)
        msg.point.y = self.radius * math.sin(self.current_angle_rad)
        msg.point.z = 0.0 # not required for 2D path following

        self.publisher.publish(msg)
        self.get_logger().debug(
            f'Published car position (angle={self.current_angle_rad:.3f} rad): '
            f'({msg.point.x:.3f}, {msg.point.y:.3f}, {msg.point.z:.3f})'
        )


def main(args=None):
    rclpy.init(args=args)
    node = CarPositionPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Car position publisher interrupted by user.')
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()




