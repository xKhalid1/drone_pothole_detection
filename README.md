Drone Detection and Inspection Project for Tuwaiq Bootcampt.

This project is an drone-based pothole detection system that uses a YOLO-based object detection model to detect road potholes using a pre-recorded video as a camera input. When a pothole is detected, pause the mission and lower the altitude and start orbiting it for close inspection before continuing the mission route.

Existing Solutions:

Manual Inspection, requires teams to physically check the road.

Cars Dashcham, high cost due to fuel and maintainace. 

Drone Systems, specialized drones like Reebot UniDrone E900, have long flight time, can deploy a swarm to cover large area. but it's mainly for taking videos then processing them later.


Challenges:
1) Duplicate detections

Same pothole detected multiple times in the same frame.

Solution:

added 500 frame detection cooldown to fix it

4) false positives

Road textures can be misclassified as potholes.

Solution:

Increased YOLO confidence threshold.


