cmake_minimum_required(VERSION 3.8)
project(serial_motor_demo)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(COMPILER_COMPATIBLE_WITH_CXX14)
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# # Bağımlılıkları buluyoruz (C++ paketleri eklendi)
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(sensor_msgs REQUIRED)

# # 1. Python Düğümlerini ve Scriptlerini Kaydediyoruz
ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  serial_motor_demo/driver_node.py
  serial_motor_demo/odom_node.py
  serial_motor_demo/laser_sync.py
  DESTINATION lib/${PROJECT_NAME}
)

# # 2. C++ Odometri Düğümünü Derliyoruz (YENİ EKLENEN KISIM)
add_executable(odom_node src/odom_node.cpp)
ament_target_dependencies(odom_node 
  rclcpp 
  std_msgs 
  geometry_msgs 
  nav_msgs 
  tf2_ros
  sensor_msgs
)

# # 3. Derlenen C++ Düğümünü Yüklüyoruz (YENİ EKLENEN KISIM)
install(TARGETS
  odom_node
  DESTINATION lib/${PROJECT_NAME}
)

# # 4. Launch, Config ve Diğer Klasörleri Paylaşılan Dizine Taşıyoruz
install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
