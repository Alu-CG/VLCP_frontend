# backend.py
from fastapi import FastAPI
from pydantic import BaseModel
import redis
import json

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class DevicePosition(BaseModel):
    name: str
    x: float
    y: float

@app.post("/update_position")
def update_position(pos: DevicePosition):
    r.set(f"device:{pos.name}", json.dumps({"x": pos.x, "y": pos.y}))
    return {"message": f"{pos.name} updated"}

@app.get("/get_all_devices")
def get_all_devices():
    keys = r.keys("device:*")
    return {
        key[7:]: json.loads(r.get(key))
        for key in keys
    }
