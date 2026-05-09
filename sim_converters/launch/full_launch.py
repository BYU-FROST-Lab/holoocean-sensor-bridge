## Holocean launch file 
# Author: Braden Meyers

from launch import LaunchDescription
import launch_ros.actions
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
from pathlib import Path

def generate_launch_description():
    print('Launching HoloOcean Vehicle Simulation')

    base = Path(get_package_share_directory('sim_converters'))
    params_file = base / 'config' / 'config.yaml'

    vehicle_namespace = 'coug0'

    # List contents of the directory to debug

    depth = launch_ros.actions.Node(
        name='depth_convert',
        package='sim_converters',
        executable='depth_convert',  
        output='screen',
        parameters=[params_file]  
    )

    gps = launch_ros.actions.Node(
        name='gps_convert',
        package='sim_converters',
        executable='gps_convert',
        output='screen',
        parameters=[params_file]  
    )

    dvl = launch_ros.actions.Node(
        name='dvl_convert',
        package='sim_converters',
        executable='dvl_convert',  
        output='screen',
        parameters=[params_file]  
    )

    imu = launch_ros.actions.Node(
        name='imu_convert',
        package='sim_converters',
        executable='imu_convert',  
        output='screen',
        parameters=[params_file]  
    )

    ucommand = launch_ros.actions.Node(
        name='u_cmd_bridge',
        package='sim_converters',
        executable='ucommand_bridge',
        output='screen',
        parameters=[params_file]  
    )

    depthr = launch_ros.actions.Node(
        name='pressure_converter',
        package='sim_converters',
        executable='depth_convert',  
        namespace=vehicle_namespace,
        output='screen',
        parameters=[params_file]  
    )

    gpsr = launch_ros.actions.Node(
        name='gps_convert',
        package='sim_converters',
        executable='gps_convert',  
        namespace=vehicle_namespace,
        output='screen',
        parameters=[params_file]  
    )

    dvlr = launch_ros.actions.Node(
        name='dvl_convert',
        package='sim_converters',
        executable='dvl_convert',  
        namespace=vehicle_namespace,
        output='screen',
        parameters=[params_file]  
    )

    imur = launch_ros.actions.Node(
        name='imu_convert',
        package='sim_converters',
        executable='imu_convert',  
        namespace=vehicle_namespace,
        output='screen',
        parameters=[params_file]  
    )

    ucommandr = launch_ros.actions.Node(
        name='u_cmd_bridge',
        package='sim_converters',
        executable='ucommand_bridge',  
        namespace=vehicle_namespace,
        output='screen',
        parameters=[params_file]  
    )

    return LaunchDescription([
        depth,
        dvl,
        gps,
        imu,
        ucommand,
        depthr,
        dvlr,
        gpsr,
        imur,
        ucommandr
    ])


