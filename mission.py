import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan


def waypoint(lat, lon, alt, speed=10.0):
    return MissionItem(
        lat,
        lon,
        alt,
        speed,
        True,
        float("nan"),
        float("nan"),
        MissionItem.CameraAction.NONE,
        float("nan"),
        float("nan"),
        float("nan"),
        float("nan"),
        float("nan"),
        MissionItem.VehicleAction.NONE
    )

async def create_mission(drone: System, waypoints):
    mission_items = []

    for waypoint in waypoints:
        mission_items.append(waypoint)

    mission_plan = MissionPlan(mission_items)

    print ("uploading mission")
    await drone.mission.upload_mission(mission_plan)
    await asyncio.sleep(2)

    print("starting mission")
    await drone.mission.start_mission()
    await asyncio.sleep(2)

mp = False

async def mission_prog(drone: System):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total:
            print("Mission completed")
            mp = True
            break