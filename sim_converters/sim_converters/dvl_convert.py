import rclpy
from rclpy.node import Node
import numpy as np
from geometry_msgs.msg import TwistWithCovarianceStamped
from dvl_msgs.msg import DVL, DVLDR
from holoocean_interfaces.msg import DVLSensorRange


class DVLConverter(Node):

    def __init__(self):
        super().__init__('dvl_converter')

        self.declare_parameter('holoocean_vehicle', 'auv0')
        holoocean_vehicle = self.get_parameter('holoocean_vehicle').get_parameter_value().string_value

        self.DVL_publisher_ = self.create_publisher(DVL, 'dvl/data', 10)
        self.DVLDR_publisher_ = self.create_publisher(DVLDR, 'dvl/position', 10)

        self.DVLVelocity_subscription = self.create_subscription(
            TwistWithCovarianceStamped,
            '/holoocean/' + holoocean_vehicle + '/DVLSensorVelocity',
            self.vel_callback,
            10)
        
        # # TODO fix this
        # self.DVLdead_reckon_subscription = self.create_subscription(
        #     PoseWithCovarianceStamped,
        #     '/holoocean/dead_reckon',
        #     self.DR_callback,
        #     10)
        
        self.dvl_range_sub = self.create_subscription(
            DVLSensorRange,
            '/holoocean/' + holoocean_vehicle + '/DVLSensorRange',
            self.altitude_callback,
            10)
        
        self.altitude = 0.0
        
 
    # def DR_callback(self, msg):
    #     publish_msg = DVLDR()
    #     publish_msg.header = msg.header
    #     # msg = Odometry()
    #     # publish_msg.position = msg.pose.pose.position
    #     # publish_msg.pos_std = msg.   //TODO: figure out where to get this data from
        
    #     # Convert quaternion to Euler angles (is this correct?)
    #     # order of the angles is z,y,x
    #     # uses r the intrinsic rotation 
    #     position_vector = Vector3()
    #     position_vector.x = msg.pose.pose.position.x
    #     position_vector.y = msg.pose.pose.position.y
    #     position_vector.z = msg.pose.pose.position.z
    #     publish_msg.position = position_vector

    #     orientation_q = msg.pose.pose.orientation
    #     orientation_list = [-orientation_q.x, orientation_q.y, orientation_q.z, -orientation_q.w]
    #     (roll, pitch, yaw) = tf_transformations.euler_from_quaternion(orientation_list, axes='rzyx')

    #     publish_msg.roll = roll
    #     publish_msg.pitch = pitch
    #     publish_msg.yaw = yaw

    #     self.DVLDR_publisher_.publish(publish_msg)

    #     # self.get_logger().info('Position: "%s"' % str(publish_msg))
    #     # self.get_logger().info('Roll: "%s"' % publish_msg.roll)
    #     # self.get_logger().info('Pitch: "%s"' % publish_msg.pitch)
    #     # self.get_logger().info('Yaw: "%s"' % publish_msg.yaw)


    def altitude_callback(self, msg: DVLSensorRange):
        # TODO handle case where not all beams hit? 
        # TODO: Fix this when we get to updating the DVL Simulation in HoloOcean
        self.altitude = float(sum(msg.range) / len(msg.range))
    
    
    def vel_callback(self, msg):
        # TODO: Fix this when we get to updating the DVL Simulation in HoloOcean
        
        publish_msg = DVL()
        publish_msg.header = msg.header
        microseconds = int((msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9) * 1e6) # convert to microseconds
        publish_msg.time_of_validity = microseconds
        publish_msg.time_of_transmission = microseconds
        publish_msg.time = 0.0 # time since last velocity report (ms)

        publish_msg.velocity.x = msg.twist.twist.linear.x
        publish_msg.velocity.y = msg.twist.twist.linear.y
        publish_msg.velocity.z = msg.twist.twist.linear.z


        # Do opposite of the reverse for covariance matrix
        covariance = np.zeros(9)
        covariance[0:3] = msg.twist.covariance[0:3]
        covariance[3:6] = msg.twist.covariance[6:9]
        covariance[6:9] = msg.twist.covariance[12:15]
        publish_msg.covariance = covariance.tolist()

        publish_msg.altitude = self.altitude

        publish_msg.velocity_valid = True 

        self.DVL_publisher_.publish(publish_msg)

 
def main(args=None):
    rclpy.init(args=args)

    node = DVLConverter()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()