from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'scan_topic',
            default_value='/tbot4_1/scan',
        ),
        DeclareLaunchArgument(
            'output_dir',
            default_value='experiment_data',
        ),
        DeclareLaunchArgument(
            'run_label',
            default_value='robot_observation',
        ),
        Node(
            package='crisis_response',
            executable='scan_observer',
            parameters=[{
                'scan_topic': LaunchConfiguration('scan_topic'),
            }],
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