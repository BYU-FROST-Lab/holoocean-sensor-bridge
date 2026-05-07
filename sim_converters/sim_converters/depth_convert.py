import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import FluidPressure

GRAVITY = 9.81  # m/s^2
FLUID_DENSITY_BASE = 997.0  # kg/m^3

class PressureConverter(Node):
    def __init__(self):
        super().__init__('pressure_converter')

        # Declare parameters
        self.declare_parameter('fluid_density', FLUID_DENSITY_BASE)
        self.declare_parameter('fluid_pressure_atm', 87250.0)
        self.declare_parameter('odometry_topic', 'depth/odom')
        self.declare_parameter('pressure_topic', 'pressure/data')

        odometry_topic = self.get_parameter('odometry_topic').get_parameter_value().string_value
        pressure_topic = self.get_parameter('pressure_topic').get_parameter_value().string_value

        # Create publisher
        self.pressure_publisher = self.create_publisher(
            FluidPressure,
            pressure_topic,
            10
        )

        # Create subscription
        self.depth_subscription = self.create_subscription(
            Odometry,
            odometry_topic,
            self.depth_callback,
            10
        )
        self.rho = self.get_parameter('fluid_density').get_parameter_value().double_value
        self.atmospheric_pressure = self.get_parameter('fluid_pressure_atm').get_parameter_value().double_value  # Optional: Add a calibration offset if needed


    def depth_callback(self, depth_msg):
        pressure_msg = FluidPressure()
        pressure_msg.header = depth_msg.header

        # Convert depth to pressure, negative downward
        depth = -depth_msg.pose.pose.position.z
        pressure = self.atmospheric_pressure + (depth * self.rho * GRAVITY)
        
        # Covariance
        pressure_msg.variance = ((self.rho * GRAVITY) ** 2) * depth_msg.pose.covariance[14]

        pressure_msg.fluid_pressure = pressure
        self.pressure_publisher.publish(pressure_msg)

def main(args=None):
    rclpy.init(args=args)
    pressure_converter = PressureConverter()
    rclpy.spin(pressure_converter)
    pressure_converter.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
