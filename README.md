# 📡VLCP_frontend

This project is a **LAN VLP device monitoring system** with a web-based frontend using **Streamlit**, a **backend API using FastAPI**, and **Redis** as the shared state store. It includes support for visualizing devices' 2D positions and displaying **VLC (Visible Light Communication)** messages.

---

## 📦 Features

- Real-time 2D scatter plot of device positions (x-y in meters)
- Fixed anchors visualization
- Auto-remove inactive devices (e.g., no update in 30s)
- VLC communication log: shows all messages sent to the server
- Manual clear button for VLC logs
- Clean separation of frontend and backend with REST APIs
- `POST /stream_adc`: Upload binary ADC data chunks (DMA streams)
- Per-device file write with safe concurrency
- Streamlit UI to:
  - 📄 List available `.bin` files
  - ⬇️ Download files
  - ❌ Delete individual or all ADC files

## WIP features:

- [x] Add a streaming API to store raw adc data to file. Support concurrency write multiple file.
- [] Show target moving trajectory.
- [] Use different color to represent different targets.
- [] Add an interface to set the position of anchors.

---

## 🧰 Technology Stack

| Component | Tech |
|----------|------|
| Frontend | [Streamlit](https://streamlit.io/) |
| Backend  | [FastAPI](https://fastapi.tiangolo.com/) |
| Storage  | [Redis](https://redis.io/) |
| Communication | HTTP (RESTful APIs) |

---

## 🚀 Getting Started
A simple frontend for Visible light positioning and visible light communication network.

Based on python streamlit framework.

### 1. Install Dependencies

```bash
pip install streamlit fastapi uvicorn redis streamlit-autorefresh
```

### 2. Start Redis

#### Option A: Local Redis

```bash
sudo apt install redis
sudo systemctl start redis
```

#### Option B: Docker

```bash
docker run -p 6379:6379 redis
```

---

### 3. Run Backend API

```bash
uvicorn backend:app --reload --port 8000
```

- `POST /update_position`: Update or add device position (with 30s expiration)
- `GET /get_all_devices`: Get current active devices
- `POST /send_vlc`: Add a VLC message (stored forever)
- `GET /get_vlc`: Get recent VLC messages
- `POST /clear_vlc`: Clear all VLC messages

---

### 4. Run Streamlit Frontend

```bash
streamlit run frontend.py
```

This launches a local web app (default: [http://localhost:8501](http://localhost:8501)) showing:

- Real-time positions of devices
- List of currently active devices
- VLC message log
- Manual "Clear VLC" button

---

## 🔬 API Testing Guide

### ➕ Add Device Position
```bash
curl -X POST http://localhost:8000/update_position \
-H "Content-Type: application/json" \
-d '{"name": "Device_A", "x": 4.2, "y": 6.1}'
```

This sets/updates a device's position and keeps it alive for 30s.

---

### 🛰️ Add VLC Message

```bash
curl -X POST http://localhost:8000/send_vlc \
-H "Content-Type: application/json" \
-d '{"content": "Light pulse received from ceiling LED"}'
```

Adds a permanent VLC message.

---

### ❌ Clear All VLC Messages

```bash
curl -X POST http://localhost:8000/clear_vlc
```

Clears all VLC messages in the system.

---

### 📡 View Current Devices (Optional)

```bash
curl http://localhost:8000/get_all_devices
```

### 🧪 Test ADC Upload

```bash
curl -X POST http://localhost:8000/stream_adc \
  -F "device_id=test_device" \
  -F "chunk=@sample_chunk.bin"
```

---

## 🧠 Notes

- Devices are **auto-removed** after 30s if not updated.
- VLC messages are stored in Redis list `vlc:messages` (newest first).
- You can easily switch Redis to another host by changing connection params in both scripts.

---

## 📁 Project Structure

```
├── backend.py        # FastAPI server with device/VLC endpoints
├── frontend.py       # Streamlit UI (2D plot + VLC log)
└── README.md         # Documentation (this file)
```
