import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
import tf2_ros
import math

class DeltaOdometryNode(Node):
    def __init__(self):
        super().__init__('real_odometry_node')
        
        # Hafıza Değişkenleri
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.last_enc = None
        self.last_imu_time = self.get_clock().now()

        # Abonelikler
        self.encoder_sub = self.create_subscription(Int32, '/odom_raw', self.encoder_callback, 10)
        self.imu_sub = self.create_subscription(Imu, '/imu/data_raw', self.imu_callback, 10)
        
        # Yayıncılar
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        
        self.get_logger().info("Jiroskop Destekli Python Odometri Motoru Aktif!")

    def imu_callback(self, msg):
        current_time = self.get_clock().now()
        dt = (current_time - self.last_imu_time).nanoseconds / 1e9
        self.last_imu_time = current_time

        if dt <= 0.0 or dt > 0.5:
            return

        # Jiroskoptan dönüş hızını alıp açıyı güncelliyoruz
        self.th += msg.angular_velocity.z * dt

    def encoder_callback(self, msg):
        current_enc = msg.data

        if self.last_enc is None:
            self.last_enc = current_enc
            return

        # Senin o kümülatif mantığın tam burada doğru deltayı hesaplıyor
        delta_enc = current_enc - self.last_enc
        self.last_enc = current_enc

        if abs(delta_enc) > 100:
            return

        # Mesafe Çarpanı (Oklar hızlı kaçarsa 0.0001 yapabilirsin)
        distance = delta_enc * 0.01

        # Robot artık döndüğü gerçek açıya göre x ve y'de ilerliyor
        self.x += distance * math.cos(self.th)
        self.y += distance * math.sin(self.th)

        current_time = self.get_clock().now().to_msg()

        # 1. TF Yayınlama (Robotu RViz'de döndüren kısım)
        t = TransformStamped()
        t.header.stamp = current_time
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = math.sin(self.th / 2.0)
        t.transform.rotation.w = math.cos(self.th / 2.0)
        self.tf_broadcaster.sendTransform(t)

        # 2. Odometry Mesajı Yayınlama
        odom = Odometry()
        odom.header.stamp = current_time
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation = t.transform.rotation
        self.odom_pub.publish(odom)

def main(args=None):
    rclpy.init(args=args)
    node = DeltaOdometryNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
