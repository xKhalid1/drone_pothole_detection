# Drone Pothole Detection and Inspection Project

## Objective

Develop an automated drone system that uses a YOLO-based object detection model to detect potholes from video feeds. When a pothole is detected, the drone temporarily pauses its mission, descends to a lower altitude, and performs an orbital inspection before resuming its predefined flight path.

---

## System Functionality

* The drone follows a predefined mission route.
* A pre-recorded video is used to simulate the onboard camera feed.
* A YOLO object detection model continuously analyzes the video stream for potholes.
* When a pothole is detected:

  1. The current mission is paused.
  2. The drone descends for closer observation.
  3. The drone performs an orbit around the pothole for detailed inspection.
  4. After inspection, the mission resumes and the drone continues along its route.

---

## Existing Solutions

### Manual Inspection

Road inspection teams physically survey roads to identify potholes.

**Advantages**

* Simple and widely used.

**Limitations**

* Time-consuming.
* Labor-intensive.
* Safety risks for personnel working near traffic.

### Vehicle-Based Systems

Dashcam-equipped vehicles capture road images for pothole detection.

**Advantages**

* Can continuously collect road data.

**Limitations**

* Fuel and maintenance costs.
* Limited accessibility in congested or hazardous areas.

## Background Analysis

| Platform          | Example             | Advantages                                                                                    | Limitations                                                                             |
| ----------------- | ------------------- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Quadcopter        | DJI Matrice 350 RTK | Can hover and perform close-range inspection; suitable for detailed infrastructure monitoring | Limited flight time and slower coverage of large road networks                          |
| VTOL / Fixed Wing | WingtraOne Gen II   | Covers large areas efficiently and is suitable for highway mapping                            | Hover mode causes the aircraft to stand upright, making close-up inspection impractical |

---

## Challenges and Solutions

| Challenge                                                              | Solution                                                                             |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Same pothole detected multiple times                                   | Implemented a 500-frame cooldown between detections to prevent duplicate inspections |
| Running object detection, flight control, and telemetry simultaneously | Used concurrent tasks                                    |
| False positives caused by road textures                                | Increased the YOLO confidence threshold to 0.85                                      |

---


# Part 2: Gazebo Simulation

## Objective

Create a Gazebo simulation to test the drone inspection behavior without using the YOLO model. Pothole detections are simulated to test how the drone reacts and performs the inspection.

---

## System Functionality

* A custom Gazebo world represents a road environment.
* The drone follows a predefined mission route.
* Pothole events are simulated.
* When a pothole event occurs:

  1. The mission pauses.
  2. The drone lowers its altitude.
  3. The drone orbits around the pothole for inspection.
  4. The drone returns to its original altitude.
  5. The mission resumes.

---

---

## Components

| X500 Drone      | Quadcopter model used in the simulation                              |
| Gimbal Camera   | Keeps the camera pointed at the inspection area                      |
| Depth Camera    | Provides depth information for future obstacle detection and mapping |
| Custom World    | Road environment with potholes                                       |

---

## Challenges and Solutions

| Challenge                                               | Solution                  |
| ------------------------------------------------------- | ------------------------- |
| No object detection model                               | Simulated pothole events  |
| Running mission control and inspection at the same time | Used concurrent tasks     |


## Setup Instructions

### 1. Download Required Assets

Download the following files:

* `world.sdf` (custom Gazebo world)
* `city_building.sdf` (building model)
* `pothole.sdf` (pothole model)

---

### 2. Place Files in PX4 Directory

Place the files in the following directories:

**World file:**

```
PX4-Autopilot/tools/simulation/gz/worlds
```

**Model files:**

```
PX4-Autopilot/tools/simulation/gz/models
```

---

### 3. Run PX4 Simulation

Run the PX4 SITL simulation using:

```bash
PX4_SYS_AUTOSTART=4019 \
PX4_GZ_MODEL_POSE="0,0,2,0,0,-45" \
PX4_SIM_MODEL=gz_x500_gd \
PX4_GZ_WORLD="external_world" \
./build/px4_sitl_default/bin/px4
```

---

### 4. Run Gazebo Scenario Script

In a new terminal, run the Python scenario script:

```bash
python3 gazebo_scenario.py
```

---

### Notes
* Run PX4 first, then start the Python script.
