import csv
from datetime import datetime, timezone
from pathlib import Path
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ExperimentLogger(Node):
    def __init__(self):
        super().__init__('experiment_logger')

        self.declare_parameter('output_dir', 'experiment_data')
        self.declare_parameter('run_label', 'simulation')

        output_dir = Path(
            self.get_parameter('output_dir').value
        ).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)

        self.run_label = self.get_parameter('run_label').value
        filename = datetime.now(timezone.utc).strftime(
            'events_%Y%m%d_%H%M%S_%f.csv'
        )
        self.path = output_dir / filename
        self.file = self.path.open(
            'x', newline='', encoding='utf-8'
        )
        self.writer = csv.writer(self.file)
        self.writer.writerow([
            'received_utc',
            'elapsed_seconds',
            'run_label',
            'topic',
            'payload',
        ])
        self.started_at = time.monotonic()
        self.file.flush()

        self.perception_sub = self.create_subscription(
            String, '/crisis/perception',
            self.on_perception, 10
        )
        self.response_sub = self.create_subscription(
            String, '/crisis/response',
            self.on_response, 10
        )

        self.get_logger().info(f'CSV saved to: {self.path.resolve()}')

    def record(self, topic, payload):
        self.writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            f'{time.monotonic() - self.started_at:.6f}',
            self.run_label,
            topic,
            payload,
        ])
        self.file.flush()

    def on_perception(self, message):
        self.record('/crisis/perception', message.data)

    def on_response(self, message):
        self.record('/crisis/response', message.data)

    def destroy_node(self):
        self.file.flush()
        self.file.close()
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ExperimentLogger()

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