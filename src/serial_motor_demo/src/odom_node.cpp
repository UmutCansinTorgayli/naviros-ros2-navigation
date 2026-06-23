#include <memory>
#include <cmath>
#include "rclpy/rclpy.hpp"
#include "std_msgs/msg/int32.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2_ros/transform_broadcaster.h"

class DeltaOdometryNode : public rclcpp::Node {
public:
    DeltaOdometryNode() : Node("real_odometry_node"), x_(0.0), y_(0.0), th_(0.0) {
        // 1. Enkoder Aboneliği
        encoder_sub_ = this->create_subscription<std_msgs::msg::Int32>(
            "/odom_raw", 10, std::bind(&DeltaOdometryNode::encoderCallback, this, std::placeholders::_1));

        // 2. 🎯 JİROSKOP (IMU) Aboneliği (Yeni Eklendi)
        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "/imu/data_raw", 10, std::bind(&DeltaOdometryNode::imuCallback, this, std::placeholders::_1));

        odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("/odom", 10);
        tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
        
        last_imu_time_ = this->now();
        RCLCPP_INFO(this->get_logger(), "Jiroskop ve Enkoder Birlesik Odometri Motoru Aktif!");
    }

private:
    // 🎯 JİROSKOP VERİSİNİ İŞLEYEN YENİ FONKSİYON
    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg) {
        rclcpp::Time current_time = this->now();
        
        // İki IMU mesajı arasında geçen gerçek süreyi (dt) hesapla
        double dt = (current_time - last_imu_time_).seconds();
        last_imu_time_ = current_time;

        // Emniyet kilidi: Süre aşırı uçuksa hesaba katma
        if (dt <= 0.0 || dt > 0.5) return;

        // Z eksenindeki dönüş hızını (radyan/sn) al ve açıya ekle
        double angular_velocity_z = msg->angular_velocity.z;
        th_ += angular_velocity_z * dt; 
    }

    void encoderCallback(const std_msgs::msg::Int32::SharedPtr msg) {
        rclcpp::Time current_time = this->now();
        double dt = 0.05; 

        int delta_enc = msg->data; 
        if (std::abs(delta_enc) > 100) return;

        // Tekerlek mesafe çarpanı (Duruma göre 0.0001 ile 0.001 arasında kalibre edebilirsin)
        double distance = delta_enc * 0.00001; 

        // 🎯 ARTIK ROBOT BAKTIĞI GERÇEK AÇIYA (th_) DOĞRU İLERLİYOR!
        x_ += distance * cos(th_);
        y_ += distance * sin(th_);

        // 1. TF Dönüşümü (Haritada robotu döndüren ve yürüten kısım)
        geometry_msgs::msg::TransformStamped odom_tf;
        odom_tf.header.stamp = current_time;
        odom_tf.header.frame_id = "odom";
        odom_tf.child_frame_id = "base_link";

        odom_tf.transform.translation.x = x_;
        odom_tf.transform.translation.y = y_;
        odom_tf.transform.translation.z = 0.0;
        
        // Açıyı kuaterniyona çevirip TF'e basıyoruz (Yön okları artık dönecek!)
        odom_tf.transform.rotation.x = 0.0;
        odom_tf.transform.rotation.y = 0.0;
        odom_tf.transform.rotation.z = sin(th_ / 2.0);
        odom_tf.transform.rotation.w = cos(th_ / 2.0);

        tf_broadcaster_->sendTransform(odom_tf);

        // 2. Standart Odometry Mesajı
        nav_msgs::msg::Odometry odom;
        odom.header.stamp = current_time;
        odom.header.frame_id = "odom";
        odom.child_frame_id = "base_link";

        odom.pose.pose.position.x = x_;
        odom.pose.pose.position.y = y_;
        odom.pose.pose.position.z = 0.0;
        
        odom.pose.pose.orientation = odom_tf.transform.rotation;
        odom.twist.twist.linear.x = distance / dt;
        odom.twist.twist.angular.z = angular_velocity_z_;

        odom_pub_->publish(odom);
    }

    rclcpp::Subscription<std_msgs::msg::Int32>::SharedPtr encoder_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_; // Yeni
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
    std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

    double x_, y_, th_;
    double angular_velocity_z_ = 0.0;
    rclcpp::Time last_imu_time_;
};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<DeltaOdometryNode>());
    rclcpp::shutdown();
    return 0;
}
