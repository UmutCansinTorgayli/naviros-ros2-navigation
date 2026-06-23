import os
from glob import glob
from setuptools import find_packages
from setuptools import setup

package_name = 'serial_motor_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')), # <--- BU SATIRI EKLE!
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='proje',
    maintainer_email='proje@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'odom_node = serial_motor_demo.odom_node:main',
            'laser_sync = serial_motor_demo.laser_sync:main',
            'teleop_wasd = serial_motor_demo.teleop_wasd:main',
	    'driver_node = serial_motor_demo.driver_node:main',
        ],
    },
)
