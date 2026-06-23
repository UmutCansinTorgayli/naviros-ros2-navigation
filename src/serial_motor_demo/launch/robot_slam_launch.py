import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Kaynak (src) altındaki gerçek yaml dosyamız
    slam_config_path = '/home/proje/ros2_ws/src/serial_motor_demo/config/mapper_lidar_only.yaml'

    # 1. Arduino Sürücü Düğümü - Artık /dev/arduino portuna kilitli!
    driver_node = Node(
        package='serial_motor_demo',
        executable='driver_node',
        name='arduino_driver_node',
        output='screen'
    )

    # 2. Odometri Düğümü
    odom_node = Node(
        package='serial_motor_demo',
        executable='odom_node',
        name='real_odometry_node',
        output='screen'
    )

    # 3. Lidar Zaman Senkronizasyon Düğümü
    laser_sync = Node(
        package='serial_motor_demo',
        executable='laser_sync',
        name='laser_sync_node',
        output='screen'
    )

    # 4. SLAM Toolbox Düğümü
    async_slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_config_path]
    )

    return LaunchDescription([
        driver_node,
        odom_node,
#        laser_sync,
    ])
