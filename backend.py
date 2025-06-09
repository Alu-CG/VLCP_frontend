# backend.py
from fastapi import FastAPI
from pydantic import BaseModel
import redis
import json
from typing import List
from fastapi import Request

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class DevicePosition(BaseModel):
    name: str
    x: float
    y: float

VLC_LIST_KEY = "vlc:messages"

class VLCMessage(BaseModel):
    content: str

@app.post("/update_position")
def update_position(pos: DevicePosition):
    key = f"device:{pos.name}"
    r.set(key, json.dumps({"x": pos.x, "y": pos.y}))
    r.expire(key, 30)  # Set key to expire in 30 seconds
    return {"message": f"{pos.name} updated"}

@app.get("/get_all_devices")
def get_all_devices():
    keys = r.keys("device:*")
    return {
        key[7:]: json.loads(r.get(key))
        for key in keys
    }

@app.post("/send_vlc")
def send_vlc_message(msg: VLCMessage):
    r.lpush(VLC_LIST_KEY, msg.content)  # Add to front
    return {"message": "VLC message stored"}

@app.get("/get_vlc")
def get_vlc_messages(limit: int = 100) -> List[str]:
    return r.lrange(VLC_LIST_KEY, 0, limit - 1)  # Latest N messages

@app.post("/clear_vlc")
def clear_vlc_messages():
    r.delete(VLC_LIST_KEY)
    return {"message": "All VLC messages cleared"}
