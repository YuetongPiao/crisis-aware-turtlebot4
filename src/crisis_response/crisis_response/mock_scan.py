import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class MockScan(Node):
    def __init__(self):
        super().__init__('mock_scan')

        self.publisher = self.create_publisher(
            LaserScan,
            '/test/scan',
            qos_profile_sensor_data,
        )

        self.started_at = time.monotonic()
        self.previous_stage = None
        self.timer = self.create_timer(0.1, self.publish_scan)

    def publish_scan(self):
        # 每20秒重复：远处 → 接近 → 突然靠近 → 离开
        elapsed = (time.monotonic() - self.started_at) % 20.0

        if elapsed < 5.0:
            stage, distance = 'CLEAR', 3.0
        elif elapsed < 10.0:
            stage, distance = 'APPROACHING', 1.2
        elif elapsed < 15.0:
            stage, distance = 'NEAR', 0.4
        else:
            stage, distance = 'CLEAR_AGAIN', 3.0

        scan = LaserScan()
        scan.header.stamp = self.get_clock().now().to_msg()
        scan.header.frame_id = 'mock_laser'

        # 361条射线，角度从-180度到+180度
        scan.angle_min = -math.pi
        scan.angle_increment = math.pi / 180.0
        scan.angle_max = math.pi
        scan.scan_time = 0.1
        scan.time_increment = 0.0
        scan.range_min = 0.12
        scan.range_max = 10.0

        ranges = [5.0] * 361

        # 正前方±10度放置模拟障碍物
        for index in range(170, 191):
            ranges[index] = distance

        scan.ranges = ranges
        self.publisher.publish(scan)

        if stage != self.previous_stage:
            self.get_logger().info(
                f'SIMULATION: {stage}, front distance={distance:.2f} m'
            )
            self.previous_stage = stage


def main(args=None):
    rclpy.init(args=args)
    node = MockScan()

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