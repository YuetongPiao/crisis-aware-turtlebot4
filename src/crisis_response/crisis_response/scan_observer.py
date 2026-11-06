import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String


class ScanObserver(Node):
    def __init__(self):
        super().__init__('scan_observer')

        self.declare_parameter('scan_topic', '/test/scan')
        topic = self.get_parameter('scan_topic').value

        self.publisher = self.create_publisher(
            String, '/crisis/perception', 10
        )
        self.subscription = self.create_subscription(
            LaserScan, topic, self.on_scan, qos_profile_sensor_data
        )

        self.last_received = None
        self.latest_distance = None
        self.latest_valid = False
        self.previous_status = None
        self.timer = self.create_timer(0.1, self.publish_status)

    def on_scan(self, scan):
        self.last_received = time.monotonic()
        distances = []

        # 提取正前方±20度，并排除无效测距值
        for index, distance in enumerate(scan.ranges):
            angle = scan.angle_min + index * scan.angle_increment
            angle = math.atan2(math.sin(angle), math.cos(angle))

            if abs(angle) <= math.radians(20):
                if (
                    math.isfinite(distance)
                    and scan.range_min <= distance <= scan.range_max
                ):
                    distances.append(distance)

        self.latest_valid = bool(distances)
        self.latest_distance = min(distances) if distances else None

    def publish_status(self):
        if self.last_received is None:
            status = 'NO_DATA'
        elif time.monotonic() - self.last_received > 1.0:
            status = 'STALE'
        elif not self.latest_valid:
            status = 'INVALID'
        else:
            status = 'VALID'

        # 无有效数据时，不沿用之前的距离
        distance = (
            f'{self.latest_distance:.3f}'
            if status == 'VALID'
            else ''
        )

        message = String()
        message.data = f'{status},{distance}'
        self.publisher.publish(message)

        if message.data != self.previous_status:
            self.get_logger().info(message.data)
            self.previous_status = message.data


def main(args=None):
    rclpy.init(args=args)
    node = ScanObserver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()