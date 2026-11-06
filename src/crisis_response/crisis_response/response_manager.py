import math
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ResponseManager(Node):
    def __init__(self):
        super().__init__('response_manager')

        # 仅用于原型测试，真机使用前需要验证
        self.declare_parameter('stop_distance', 0.6)
        self.declare_parameter('warning_distance', 1.5)
        self.declare_parameter('clear_distance', 1.8)
        self.declare_parameter('clear_hold_seconds', 2.0)
        self.declare_parameter('perception_timeout', 0.5)

        self.stop_distance = self.get_parameter('stop_distance').value
        self.warning_distance = self.get_parameter('warning_distance').value
        self.clear_distance = self.get_parameter('clear_distance').value
        self.hold_seconds = self.get_parameter('clear_hold_seconds').value
        self.timeout = self.get_parameter('perception_timeout').value

        if not (
            0 < self.stop_distance
            < self.warning_distance
            < self.clear_distance
            and self.hold_seconds > 0
            and self.timeout > 0
        ):
            raise ValueError('Invalid distance or timing parameters')

        self.publisher = self.create_publisher(
            String, '/crisis/response', 10
        )
        self.subscription = self.create_subscription(
            String, '/crisis/perception', self.on_perception, 10
        )

        self.last_received = None
        self.distance = None
        self.data_status = 'NO_DATA'
        self.stop_latched = True
        self.clear_since = None
        self.previous_output = None
        self.timer = self.create_timer(0.1, self.evaluate)

    def on_perception(self, message):
        self.last_received = time.monotonic()
        self.distance = None

        try:
            status, value = message.data.split(',', 1)

            if status == 'VALID':
                distance = float(value)
                if not math.isfinite(distance) or distance < 0:
                    raise ValueError('Invalid distance')
                self.distance = distance
                self.data_status = 'VALID'
            elif status in ('NO_DATA', 'STALE', 'INVALID'):
                self.data_status = status
            else:
                self.data_status = 'INVALID'
        except (ValueError, TypeError):
            self.data_status = 'INVALID'

        # 接收时也锁存危险，避免短暂危险被下一条消息覆盖
        if (
            self.data_status != 'VALID'
            or self.distance <= self.stop_distance
        ):
            self.stop_latched = True
            self.clear_since = None
        elif self.distance < self.clear_distance:
            self.clear_since = None

    def evaluate(self):
        now = time.monotonic()

        if self.last_received is None:
            status = 'NO_DATA'
        elif now - self.last_received > self.timeout:
            status = 'PERCEPTION_TIMEOUT'
        else:
            status = self.data_status

        if status != 'VALID':
            self.stop_latched = True
            self.clear_since = None
            risk, action, reason = 'UNKNOWN', 'STOP', status

        elif self.distance <= self.stop_distance:
            self.stop_latched = True
            self.clear_since = None
            risk, action, reason = 'HIGH', 'STOP', 'NEAR_OBSTACLE'

        elif self.stop_latched:
            if self.distance >= self.clear_distance:
                if self.clear_since is None:
                    self.clear_since = now

                if now - self.clear_since >= self.hold_seconds:
                    self.stop_latched = False
                    risk, action, reason = (
                        'LOW', 'READY', 'CLEAR_CONFIRMED'
                    )
                else:
                    risk, action, reason = (
                        'LOW', 'HOLD', 'CONFIRMING_CLEAR'
                    )
            else:
                self.clear_since = None
                risk = (
                    'MEDIUM'
                    if self.distance <= self.warning_distance
                    else 'LOW'
                )
                action, reason = 'HOLD', 'WAITING_FOR_CLEARANCE'

        elif self.distance <= self.warning_distance:
            risk, action, reason = (
                'MEDIUM', 'CAUTION', 'OBSTACLE_APPROACHING'
            )
        else:
            risk, action, reason = 'LOW', 'READY', 'CLEAR'

        distance_text = (
            f'{self.distance:.3f}' if status == 'VALID' else ''
        )

        message = String()
        message.data = f'{risk},{action},{reason},{distance_text}'
        self.publisher.publish(message)

        output_key = (risk, action, reason)
        if output_key != self.previous_output:
            self.get_logger().info(message.data)
            self.previous_output = output_key


def main(args=None):
    rclpy.init(args=args)
    node = ResponseManager()

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