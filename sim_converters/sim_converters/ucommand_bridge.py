import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from holoocean_interfaces.msg import AgentCommand
from cougars_interfaces.msg import ActuatorCommand
import math


class ActuatorCommandBridge(Node):
    def __init__(self):
        super().__init__('u_cmd_bridge')

        # Declare parameters
        self.declare_parameter('holoocean_vehicle', 'auv0')
        self.declare_parameter('fin_scalar', 1.0)
        self.declare_parameter('publish_thruster', False)

        # Get parameter values
        self.holoocean_vehicle = self.get_parameter('holoocean_vehicle').get_parameter_value().string_value
        self.fin_scalar = self.get_parameter('fin_scalar').get_parameter_value().double_value
        self.publish_thruster = self.get_parameter('publish_thruster').get_parameter_value().bool_value

        # Construct topic names from parameters
        holoocean_pub_topic = f'/holoocean/command/agent'
        vehicle_topic = 'control/u_cmd'

        # Subscriptions
        self.u_cmd_sub = self.create_subscription(
            ActuatorCommand,
            vehicle_topic,
            self.u_cmd_callback,
            10
        )

        self.holoocean_sub = self.create_subscription(
            AgentCommand,
            '/holoocean/' + self.holoocean_vehicle + '/ControlCommand',
            self.holoocean_callback,
            10
        )

        # Publishers
        self.u_cmd_pub = self.create_publisher(
            ActuatorCommand,
            vehicle_topic,
            10
        )

        self.holoocean_pub = self.create_publisher(
            AgentCommand,
            holoocean_pub_topic,
            10
        )

    def u_cmd_callback(self, msg: ActuatorCommand):
        # If this was sent from the bridge ignore the passing back to holoocean
        if msg.header.frame_id == "holoocean_to_frost":
            return

        # Convert fin angles from degrees to radians
        fins_rad = [-1 * math.radians(angle) for angle in msg.fin[:3]]

        # Thruster percentage directly used
        # TODO map thruster values from 0-100 to 0-1500 rpm which is not linear
        thruster = float(msg.thruster) * 15 

        # Pack into CommandControl message
        control_msg = AgentCommand()
        control_msg.header = Header()
        control_msg.header.stamp = self.get_clock().now().to_msg()
        control_msg.header.frame_id = self.holoocean_vehicle
        control_msg.command = fins_rad + [thruster]



        self.holoocean_pub.publish(control_msg)

    def holoocean_callback(self, msg: AgentCommand):
        if len(msg.command) < 3:
            self.get_logger().warn("AgentCommand message has fewer than 3 fins")
            return

        # Convert fin angles from radians to degrees and apply scalar
        fins_deg = [math.degrees(angle) * self.fin_scalar for angle in msg.command[:3]]

        u_cmd_msg = ActuatorCommand()
        u_cmd_msg.header = Header()
        u_cmd_msg.header.stamp = self.get_clock().now().to_msg()
        u_cmd_msg.header.frame_id = "holoocean_to_frost"
        u_cmd_msg.fin = fins_deg + [0.0]  # Pad with unused value

        # Thruster: only publish if enabled

        u_cmd_msg.thruster = int(msg.command[3]) if (self.publish_thruster and len(msg.command) >= 4) else 0

        # TODO: Need to figure out how to handle when running holoocean commands
        # TODO make this not work for right now
        # self.u_cmd_pub.publish(u_cmd_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ActuatorCommandBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
