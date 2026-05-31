import asyncio
from mavsdk import System
import cv2
import functions2
import mission


pothole_event = asyncio.Event()

cap = None
frame_count = 0
last_detection_frame = -999

async def pothole_detection(drone: System):
    global cap, frame_count, last_detection_frame
    cap = cv2.VideoCapture("pothole3.mp4")
    frame_count = 0

    while True:
        await asyncio.sleep(0)

        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 10 != 0:
            continue
        
        #pause the video if pothole is detected at current frame and wait for inspection to complete
        if pothole_event.is_set():
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
            frame_count -= 1
            await asyncio.sleep(0.1)
            continue

        results = functions2.model(frame, conf=0.85, verbose=False)
        annotated = results[0].plot()

        if len(results[0].boxes) > 0 and (frame_count - last_detection_frame) > 500: #500 is to stop the detection from triggering multiple times for the same pothole
            print(f"Pothole detected at frame {frame_count}, starting pothole inspection")
            last_detection_frame = frame_count
            pothole_event.set()

        annotated = cv2.resize(annotated, (500, 540))
        cv2.imshow("pothole Inspection", annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


async def pothole_inspection(drone: System):
    global cap, frame_count
    while True:
        await pothole_event.wait()

        await drone.mission.pause_mission()
        await asyncio.sleep(1)

        current_lat = functions2.cur_pos.latitude_deg
        current_lon = functions2.cur_pos.longitude_deg
        current_alt = functions2.cur_pos.relative_altitude_m
        print(f"Orbiting pothole at: {current_lat, current_lon, current_alt}")

        await functions2.orbit(drone, 5, 3, current_lat, current_lon, current_alt - 5)

        await functions2.wait_orbit(
            drone,
            center_lat=current_lat,
            center_lon=current_lon,
            radius_m=5,
        )

        await drone.action.hold()
        await asyncio.sleep(1)
        await drone.mission.start_mission()

        pothole_event.clear()


async def run():
    drone = System()
    await functions2.connect(drone)

    home = await anext(drone.telemetry.home())
    alt = home.absolute_altitude_m
    lat = home.latitude_deg
    long = home.longitude_deg

    fly_alt = alt + 10
    print(f"home location", lat, long, alt)

    await functions2.arm(drone)
    await functions2.takeoff(drone, fly_alt)

    waypoints = []
    for i in range(1):
        x = 10 * (i + 1)
        y = 7 * (i + 1)
        waypoints.append(
            mission.waypoint(lat + x * 10e-5, long - y * 10e-5, fly_alt)
        )

    await mission.create_mission(drone, waypoints)

    pos_task        = asyncio.create_task(functions2.position(drone))
    mission_task    = asyncio.create_task(mission.mission_prog(drone))
    inspection_task = asyncio.create_task(pothole_inspection(drone))
    detection_task  = asyncio.create_task(pothole_detection(drone))

    await mission_task

    inspection_task.cancel()
    detection_task.cancel()
    pos_task.cancel()
    mission_task.cancel()

    await drone.action.return_to_launch()
    await functions2.check_position(drone, lat, long)
    await functions2.land(drone)

asyncio.run(run())