import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import select
import tty
import termios

settings = termios.tcgetattr(sys.stdin)

msg = """
=============================================
     LİDAR VE SLAM İÇİN SABİT WASD MODU
=============================================
                  [W] : İleri Gidiş
   [A] : Sola Dönüş             [D] : Sağa Dönüş
                  [S] : Geri Gidiş

                  [X] : KESİN DUR (FREN)

* Ağırlığı yenmek için tork sürücüde maksimuma ayarlandı.
* Çıkış için CTRL+C yapın.
=============================================
"""

def get_key():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

class TeleopWASD(Node):
    def __init__(self):
        super().__init__('teleop_wasd_node')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Sürücüye gönderilecek sabit adımlı komutlar
        self.FIXED_SPEED = 0.5  
        self.FIXED_TURN = 0.5   
        
        print(msg)
        self.timer = self.create_timer(0.1, self.run_teleop)

    def run_teleop(self):
        key = get_key()
        twist = Twist()
        
        if key == 'w':
            twist.linear.x = self.FIXED_SPEED
            self.publisher_.publish(twist)
        elif key == 's':
            twist.linear.x = -self.FIXED_SPEED
            self.publisher_.publish(twist)
        elif key == 'a':
            twist.angular.z = self.FIXED_TURN
            self.publisher_.publish(twist)
        elif key == 'd':
            twist.angular.z = -self.FIXED_TURN
            self.publisher_.publish(twist)
        elif key == 'x':
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.publisher_.publish(twist)
        elif key == '\x03': 
            sys.exit(0)

def main(args=None):
    rclpy.init(args=args)
    node = TeleopWASD()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
