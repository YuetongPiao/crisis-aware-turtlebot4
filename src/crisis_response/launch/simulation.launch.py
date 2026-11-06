from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'output_dir',
            default_value='/workspaces/crisis_robot_ws/experiment_data',
        ),
        DeclareLaunchArgument(
            'run_label',
            default_value='simulation_launch',
        ),
        Node(
            package='crisis_response',
            executable='mock_scan',
            output='screen',
        ),
        Node(
            package='crisis_response',
            executable='scan_observer',
            parameters=[{'scan_topic': '/test/scan'}],
            output='screen',
        ),
        Node(
            package='crisis_response',
            executable='response_manager',
            output='screen',
        ),
        Node(
            package='crisis_response',
            executable='experiment_logger',
            parameters=[{
                'output_dir': LaunchConfiguration('output_dir'),
                'run_label': LaunchConfiguration('run_label'),
            }],
            output='screen',
        ),
    ])