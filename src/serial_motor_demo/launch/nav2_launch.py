import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    package_name = 'serial_motor_demo'
    
    # Bizim hazırladığımız hafifletilmiş yaml dosyasının yolu
    nav2_params_path = os.path.join(
        get_package_share_directory(package_name),
        'config',
        'nav2_params.yaml'
    )
    
    # ROS2 Nav2 sisteminin orijinal getirme launch dizini
    nav2_launch_dir = os.path.join(
        get_package_share_directory('nav2_bringup'),
        'launch'
    )
    
    return LaunchDescription([
        # Nav2 navigasyon sunucularını bizim parametrelerimizle tetikliyoruz
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'navigation_launch.py')),
            launch_arguments={
                'use_sim_time': 'False',
                'params_file': nav2_params_path
            }.items()
        )
    ])
