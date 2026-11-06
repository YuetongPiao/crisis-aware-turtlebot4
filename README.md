# Crisis-aware TurtleBot4

ROS 2 Humble obstacle-response prototype.

## Current scope

Processes a forward LiDAR sector and publishes response recommendations.
It does not send robot motion commands.
Depth-camera integration and real-robot validation remain pending.

## Nodes

- mock_scan: publishes simulated LaserScan messages on /test/scan.
- scan_observer: publishes distance and data-validity status on /crisis/perception.
- response_manager: publishes risk and response states on /crisis/response.
- experiment_logger: records perception and response messages to CSV.

## Build

Run inside a ROS 2 Humble environment, from the workspace root:

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select crisis_response
source install/setup.bash
```

## Simulation

```bash
ros2 launch crisis_response simulation.launch.py
```

## Real-robot observation

Connect to the robot's ROS network first:

```bash
ros2 launch crisis_response robot_observation.launch.py scan_topic:=/tbot4_1/scan run_label:=robot_observation
```

Stop an active launch with Ctrl+C before starting another.
Check for duplicate nodes with ros2 node list.

## Tests completed on 2026-11-06

Simulation and injected perception-message tests demonstrated:

- Approaching obstacle: CAUTION.
- Near obstacle: STOP.
- Missing perception messages: STOP with PERCEPTION_TIMEOUT.
- Invalid numeric distance (nan): STOP with INVALID.
- After a stop, 1.7 m remains HOLD.
- At 1.8 m, sustained clearance allows READY after approximately 2 seconds.
- At 0.6 m, the response is STOP.
- No robot input at startup: STOP with NO_DATA.

## Experiment records

CSV timestamps represent receipt at the logger, not physical braking time.
Message rows are not independent experimental trials.

- events_20261106_170911_384582.csv:
  exploratory run; duplicate decision publishers were discovered.
- events_20261106_173351_209598.csv:
  exploratory invalid-input and boundary tests; duplicate publishers
  were still present.
- events_20261106_180930_361886.csv:
  single-manager retest; 9,784 message records.
- events_20261106_183148_568177.csv:
  launch debugging run; earlier nodes had not been cleared.
- events_20261106_183410_678922.csv:
  simulation launch check after clearing earlier nodes.
- events_20261106_184005_234284.csv:
  home startup check without a robot; NO_DATA expected.

Keep exploratory records separate from the single-manager retest
when analysing results.

## Next school session

1. Transfer the source and build in the school's Humble container.
2. Confirm /tbot4_1/scan is publishing.
3. Start robot_observation.launch.py once.
4. Keep the robot stationary and verify that an obstacle in front
   changes the measured forward distance.
5. Record approach, near-obstacle and clearance responses.
6. Save CSV files, screenshots, measured obstacle positions and notes.
7. Check the OAK-D camera state with the teacher; depth output is
   not yet verified.