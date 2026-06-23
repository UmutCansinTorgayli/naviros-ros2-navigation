import rclpy 
from rclpy.node import Node 
from std_msgs.msg import Int32 
from sensor_msgs.msg import Imu 
from geometry_msgs.msg import Twist 
import serial 
import time 

class ArduinoDriverNode(Node): 
    def __init__(self): 
        super().__init__('arduino_driver_node') 
         
        # Seri Port Bağlantısı (Orijinal 9600 Hızın Aynen Korundu) 
        try: 
            self.ser = serial.Serial('/dev/arduino', 9600, timeout=0.05) 
            self.get_logger().info("Arduino'ya başarıyla bağlanıldı!") 
        except Exception as e: 
            self.get_logger().error(f"Seri port açılamadı: {e}") 
            return 

        # Yayıncılar (Publishers - Aynen Korundu) 
        self.encoder_pub = self.create_publisher(Int32, '/odom_raw', 10) 
        self.imu_pub = self.create_publisher(Imu, '/imu/data_raw', 10) 

        # Abonelik (Klavye/WASD ve Nav2 Kontrolü İçin) 
        self.cmd_sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10) 

        # Seri Okuma Zamanlayıcısı (20Hz - Her 50ms'de bir) 
        self.timer = self.create_timer(0.05, self.read_serial) 

    def cmd_callback(self, msg): 
        linear = msg.linear.x 
        angular = msg.angular.z 
         
        # 🛡️ KESİN GÜVENLİK FİLTRESİ (Uçup gitmeyi engelleyen satır) 
        # Eğer Nav2 veya teleop gerçekten DUR (0.0) diyorsa, hiçbir hesaba girmeden 
        # doğrudan motorları sıfırlıyoruz ve fonksiyonu bitiriyoruz! 
        if abs(linear) < 0.001 and abs(angular) < 0.001: 
            cmd_str = "M,0,0\n" 
            try: 
                self.ser.write(cmd_str.encode()) 
            except: 
                pass 
            return  # Alttaki tork hilesine girmeden burada kes! 

        # 🚀 OTONOM KALKIŞ TORK HİLESİ (Sadece robot gerçekten hareket etmek isterse) 
        if linear > 0.01: 
            linear = 0.5 
        elif linear < -0.01: 
            linear = -0.5 

        if angular > 0.01: 
            angular = 0.5 
        elif angular < -0.01: 
            angular = -0.5 
         
        # Sizin orijinal PWM çarpanlarınız 
        sol_pwm = int((linear * 150) - (angular * 100)) 
        sag_pwm = int((linear * 150) + (angular * 100)) 
         
        # Sınırlandırma (-255, 255) 
        sol_pwm = max(min(sol_pwm, 255), -255) 
        sag_pwm = max(min(sag_pwm, 255), -255) 

        cmd_str = f"M,{sol_pwm},{sag_pwm}\n" 
        try: 
            self.ser.write(cmd_str.encode()) 
        except: 
            pass 

    def read_serial(self): 
        if self.ser.in_waiting > 0: 
            try: 
                line = self.ser.readline().decode('utf-8').strip() 
                 
                if "Enc:" in line and "GyroZ:" in line: 
                    parts = line.split('|') 
                     
                    # 1. Enkoder Değerini Ayıkla 
                    enc_val = int(parts[0].split(':')[1].strip()) 
                    enc_msg = Int32() 
                    enc_msg.data = enc_val 
                    self.encoder_pub.publish(enc_msg) 

                    # 2. GyroZ Değerini Ayıkla 
                    gyro_z_deg = float(parts[3].split(':')[1].strip()) 
                    gyro_z_rad = gyro_z_deg * (3.14159265 / 180.0) 

                    # Standart ROS2 IMU Mesajını Doldur 
                    imu_msg = Imu() 
                    imu_msg.header.stamp = self.get_clock().now().to_msg() 
                    imu_msg.header.frame_id = 'base_link' 
                    imu_msg.angular_velocity.z = gyro_z_rad 

                    self.imu_pub.publish(imu_msg) 
            except: 
                pass 

def main(args=None): 
    rclpy.init(args=args) 
    node = ArduinoDriverNode() 
    rclpy.spin(node) 
    node.destroy_node() 
    rclpy.shutdown() 

if __name__ == '__main__': 
    main()
