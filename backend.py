# backend.py
from pathlib import Path
from fastapi import Query
from pydantic import BaseModel
import redis
import json
from typing import List
from fastapi import Request

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
import aiofiles
import os
import time
import asyncio
from typing import Dict

app = FastAPI()
DATA_DIR = "adc_data"
os.makedirs(DATA_DIR, exist_ok=True)

# Per-device lock dictionary
device_locks: Dict[str, asyncio.Lock] = {}

def get_device_lock(device_id: str) -> asyncio.Lock:
    if device_id not in device_locks:
        device_locks[device_id] = asyncio.Lock()
    return device_locks[device_id]

@app.post("/stream_adc")
async def stream_adc(device_id: str = Form(...), chunk: UploadFile = File(...)):
    if not device_id or not chunk:
        return JSONResponse(status_code=400, content={"message": "Missing device_id or file chunk"})

    filename = os.path.join(DATA_DIR, f"adc_{device_id}.bin")
    lock = get_device_lock(device_id)

    try:
        async with lock:
            async with aiofiles.open(filename, "ab") as f:
                while True:
                    content = await chunk.read(4096)
                    if not content:
                        break
                    await f.write(content)
        return {"message": f"Data written to {filename}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

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

@app.delete("/delete_adc_file")
def delete_adc_file(device_id: str = Query(...)):
    file_path = Path("adc_data") / f"adc_{device_id}.bin"
    if file_path.exists():
        file_path.unlink()
        return {"message": f"{file_path.name} deleted"}
    return {"error": "File not found"}
