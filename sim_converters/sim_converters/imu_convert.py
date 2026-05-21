#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from collections import deque

MAX_QUEUE = 5
TIME_TOL = 0.01  # 10ms match tolerance

def _stamp_sec(stamp):
    return stamp.sec + stamp.nanosec * 1e-9

def _find_match(queue, target_stamp):
    """Return index of closest message within TIME_TOL, or None."""
    target_t = _stamp_sec(target_stamp)
    best_idx, best_dt = None, float('inf')
    for i, msg in enumerate(queue):
        dt = abs(_stamp_sec(msg.header.stamp) - target_t)
        if dt < TIME_TOL and dt < best_dt:
            best_dt, best_idx = dt, i
    return best_idx


class ImuCombiner(Node):
    def __init__(self):
        super().__init__('imu_combiner')

        self.declare_parameter('imu_topic', '/holoocean/coug0/IMUSensor')
        self.declare_parameter('orientation_topic', '/holoocean/coug0/DynamicsSensorIMU')
        self.declare_parameter('output_topic', 'sim/imu/data')
        imu_topic = self.get_parameter('imu_topic').value
        orientation_topic = self.get_parameter('orientation_topic').value
        output_topic = self.get_parameter('output_topic').value

        self.orientation_queue = deque(maxlen=MAX_QUEUE)
        self.imu_queue = deque(maxlen=MAX_QUEUE)

        self.orientation_sub = self.create_subscription(
            Imu,
            orientation_topic,
            self.orientation_callback,
            10)

        self.imu_sub = self.create_subscription(
            Imu,
            imu_topic,
            self.imu_callback,
            10)

        self.publisher = self.create_publisher(Imu, output_topic, 10)

    def orientation_callback(self, msg):
        idx = _find_match(self.imu_queue, msg.header.stamp)
        if idx is not None:
            imu_msg = self.imu_queue[idx]
            del self.imu_queue[idx]
            self._publish(msg, imu_msg)
        else:
            self.orientation_queue.append(msg)

    def imu_callback(self, msg):
        idx = _find_match(self.orientation_queue, msg.header.stamp)
        if idx is not None:
            dyn_msg = self.orientation_queue[idx]
            del self.orientation_queue[idx]
            self._publish(dyn_msg, msg)
        else:
            self.imu_queue.append(msg)

    def _publish(self, orientation_msg, imu_msg):
        out = Imu()
        out.header = imu_msg.header
        out.orientation = orientation_msg.orientation
        out.orientation_covariance = orientation_msg.orientation_covariance
        out.linear_acceleration = imu_msg.linear_acceleration
        out.linear_acceleration_covariance = imu_msg.linear_acceleration_covariance
        out.angular_velocity = imu_msg.angular_velocity
        out.angular_velocity_covariance = imu_msg.angular_velocity_covariance
        self.publisher.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = ImuCombiner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
