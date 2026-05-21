#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from dvl_msgs.msg import DVLDR


def _quaternion_to_euler(x, y, z, w):
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = max(-1.0, min(1.0, 2.0 * (w * y - z * x)))
    pitch = math.asin(sinp)

    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw


class OdomToDVLDR(Node):
    def __init__(self):
        super().__init__('odom_to_dvldr')

        self.declare_parameter('input_topic', 'odometry/dvl')
        self.declare_parameter('output_topic', 'dvl/position')
        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        self.pub = self.create_publisher(DVLDR, output_topic, 10)
        self.sub = self.create_subscription(
            Odometry, input_topic, self._callback, 10)

    def _callback(self, msg: Odometry):
        out = DVLDR()
        # TODO look into the output of this. 
        out.header = msg.header
        out.child_frame_id = msg.child_frame_id

        t = msg.header.stamp
        out.time = float(t.sec) + t.nanosec * 1e-9

        out.position.x = msg.pose.pose.position.x
        out.position.y = msg.pose.pose.position.y
        out.position.z = msg.pose.pose.position.z

        # pos_std: mean of the three position axis standard deviations
        # pose.covariance is a 6x6 matrix stored row-major (36 elements)
        # diagonal indices for x, y, z are 0, 7, 14
        cov = msg.pose.covariance
        std_x = math.sqrt(abs(cov[0]))
        std_y = math.sqrt(abs(cov[7]))
        std_z = math.sqrt(abs(cov[14]))
        out.pos_std = (std_x + std_y + std_z) / 3.0

        q = msg.pose.pose.orientation
        roll, pitch, yaw = _quaternion_to_euler(q.x, q.y, q.z, q.w)
        out.roll = math.degrees(roll)
        out.pitch = math.degrees(pitch)
        out.yaw = math.degrees(yaw)

        out.type = 'position_local'
        out.status = 0
        out.format = 'json_v3'

        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = OdomToDVLDR()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
