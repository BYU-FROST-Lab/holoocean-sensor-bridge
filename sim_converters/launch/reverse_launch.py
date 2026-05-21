## Holocean launch file 
# Author: Braden Meyers

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from pathlib import Path
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    print('Launching HoloOcean Vehicle Simulation')

    base = Path(get_package_share_directory('sim_converters'))
    params_file = base / 'config' / 'config.yaml'
    
    sim = LaunchConfiguration('sim')
    # todo FIX hardcoded namespace
    vehicle_namespace = 'coug0'

    return LaunchDescription([
        DeclareLaunchArgument(
            'sim',
            default_value='False'
        ),
        Node(
            name='pressure_converter',
            package='sim_converters',
            executable='depth_convert',  
            namespace=vehicle_namespace,
            output='screen',
            parameters=[params_file, {'use_sim_time': sim}]  
        ),
        Node(
            name='dvl_converter_node',
            package='holoocean_bridge',
            executable='dvl_converter',  
            namespace=vehicle_namespace,
            output='screen',
            parameters=[params_file, {'use_sim_time': sim}]
        ),
        Node(
            name='gps_convert',
            package='sim_converters',
            executable='gps_convert',  
            namespace=vehicle_namespace,
            output='screen',
            parameters=[params_file, {'use_sim_time': sim}]  
        ),
        Node(
            name='u_cmd_bridge',
            package='sim_converters',
            executable='ucommand_bridge',  
            namespace=vehicle_namespace,
            output='screen',
            parameters=[params_file, {'use_sim_time': sim}]  
        ),
        Node(
            package='robot_localization', 
            executable='ekf_node', 
            name='ekf_filter_node_odom',
            namespace=vehicle_namespace,
            output='screen',
            parameters=[params_file, {'use_sim_time': sim}],
            remappings=[('odometry/filtered', 'odometry/dvl')]           
        ),
        Node(
            name='odom_to_dvldr',
            package='sim_converters',
            executable='odom_to_dvldr',
            namespace=vehicle_namespace,
            output='screen',
            parameters=[params_file, {'use_sim_time': sim}]
        ),
        Node(
            package='topic_tools',
            name='sim_imu_source',
            executable='relay',
            parameters=[params_file, {'use_sim_time': sim}],
            namespace=vehicle_namespace,
        ),
    ])


