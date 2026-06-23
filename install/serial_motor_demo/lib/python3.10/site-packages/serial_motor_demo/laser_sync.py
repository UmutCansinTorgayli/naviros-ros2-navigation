import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class LaserSyncNode(Node):
    def __init__(self):
        super().__init__('laser_sync_node')
        # Ham /scan başlığını dinliyoruz
        self.sub = self.create_subscription(LaserScan, '/scan', self.callback, 10)
        # Zamanı eşitlenmiş /scan_sync başlığını basıyoruz
        self.pub = self.create_publisher(LaserScan, '/scan_sync', 10)
        self.get_logger().info("Lidar Zaman Senkronizasyon Dugumu Aktif!")

    def callback(self, msg):
        try:
            # Yeni bir mesaj nesnesi oluşturup eski verileri kopyalıyoruz
            sync_msg = msg
            # Zaman damgasını zorla anlık canlı işlemci saatine eşitliyoruz
            sync_msg.header.stamp = self.get_clock().now().to_msg()
            self.pub.publish(sync_msg)
        except Exception as e:
            self.get_logger().error(f"Hata olustu: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = LaserSyncNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
