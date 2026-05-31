import asyncio
import time
from mavsdk import System
from mavsdk.action import OrbitYawBehavior
from mavsdk.telemetry import LandedState
from ultralytics import YOLO
import math

model = YOLO("my_model(1).pt")

def run_yolo_on_frame(frame):
    return model(frame, verbose=False)


async def connect(drone: System):
    print("Connecting to drone")
    await drone.connect(system_address="udpin://0.0.0.0:14540")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break

async def arm(drone: System):
    print("arming the drone")
    await drone.action.arm()
    async for armed in drone.telemetry.armed():
        if armed:
            print("the drone is armed")
            break

async def takeoff(drone: System, target):
    print("taking off")
    await drone.action.set_takeoff_altitude(target)
    await drone.action.takeoff()
    async for state in drone.telemetry.landed_state():
        if state == LandedState.IN_AIR:
            await check_altitude(drone, target)
            print("takeoff success")
            break


async def land(drone: System):
    print("landing")
    await drone.action.land()
    async for state in drone.telemetry.landed_state():
        if state == LandedState.ON_GROUND:
            print("Landing success")
            break

cur_pos = None

async def position(drone: System):
    global cur_pos
    async for position in drone.telemetry.position():
        cur_pos = position


async def check_altitude(drone: System, target):
    async for position in drone.telemetry.position():
        if position.relative_altitude_m >= target-1:
            print("Reached target altitude.")
            break

async def check_position(drone: System, lat, long):
    async for position in drone.telemetry.position():
        if (position.latitude_deg >= (lat - 0.00005) and position.latitude_deg <= (lat + 0.00005)
        and position.longitude_deg >= (long - 0.00005) and position.longitude_deg <= (long + 0.00005)):
            print("Reached target position.")
            break

async def orbit(drone: System, radius, speed, latitude, longitude, altitude):
    print("starting orbit")
    await drone.action.do_orbit(
        radius,
        speed,
        OrbitYawBehavior.HOLD_FRONT_TO_CIRCLE_CENTER,
        latitude,
        longitude,
        altitude
    )


async def wait_orbit(drone: System,
                     center_lat: float,
                     center_lon: float,
                     radius_m: float,
                     circle_tolerance_m: float = 1.0,
                     start_tolerance_deg: float = 10 * 1e-6):

    def distance_m(lat1, lon1, lat2, lon2):
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # 1) Wait until we are on the orbit circle
    print("Waiting for drone to reach orbit circle...")
    async for position in drone.telemetry.position():
        d = distance_m(center_lat, center_lon,
                       position.latitude_deg, position.longitude_deg)
        if abs(d - radius_m) <= circle_tolerance_m:
            start_lat = position.latitude_deg
            start_lon = position.longitude_deg
            print("Orbit started")
            break

    # 2) Wait until it leaves the start region
    async for position in drone.telemetry.position():
        if (abs(position.latitude_deg - start_lat) > start_tolerance_deg or
                abs(position.longitude_deg - start_lon) > start_tolerance_deg):
            print("Left start point, orbit in progress...")
            break

    # 3) Wait until it comes back — with the wider tolerance this now reliably
    #    triggers on the first pass rather than requiring a second lap
    print("Waiting for drone to complete one full orbit...")
    async for position in drone.telemetry.position():
        if (abs(position.latitude_deg - start_lat) <= start_tolerance_deg and
                abs(position.longitude_deg - start_lon) <= start_tolerance_deg):
            print("One full orbit completed!")
            break