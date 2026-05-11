## Holocean launch file 
# Author: Braden Meyers

from launch import LaunchDescription
import launch_ros.actions
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
from pathlib import Path
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    print('Launching HoloOcean Vehicle Simulation')

    base = Path(get_package_share_directory('sim_converters'))
    params_file = base / 'config' / 'config.yaml'
    use_sim_time_launch_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='False'
    )
    use_sim_time = LaunchConfiguration('use_sim_time')

    # List contents of the directory to debug

    depth = launch_ros.actions.Node(
        name='depth_convert',
        package='sim_converters',
        executable='depth_convert',  
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]  
    )

    gps = launch_ros.actions.Node(
        name='gps_convert',
        package='sim_converters',
        executable='gps_convert',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]  
    )

    dvl = launch_ros.actions.Node(
        name='dvl_convert',
        package='sim_converters',
        executable='dvl_convert',  
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]  
    )

    imu = launch_ros.actions.Node(
        name='imu_convert',
        package='sim_converters',
        executable='imu_convert',  
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]  
    )

    ucommand = launch_ros.actions.Node(
        name='u_cmd_bridge',
        package='sim_converters',
        executable='ucommand_bridge',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]  
    )


    return LaunchDescription([
        use_sim_time_launch_arg,
        depth,
        dvl,
        gps,
        imu,
        ucommand,
    ])


