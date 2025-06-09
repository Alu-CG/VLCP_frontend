import streamlit as st
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh
import altair as alt

st.set_page_config(page_title="LAN Device Tracker", layout="wide")
st.title("📡 LAN Device Tracker with VLC Monitor")

# Refresh every 5 seconds
st_autorefresh(interval=5000, key="auto_refresh")

# Anchor positions (fixed in 2D space, e.g., corners of a 10x10 room)
anchors = {
    "Anchor_1": {"x": 0, "y": 0},
    "Anchor_2": {"x": 10, "y": 0},
    "Anchor_3": {"x": 0, "y": 10},
    "Anchor_4": {"x": 10, "y": 10},
}

# Initialize devices if not already done
if "devices" not in st.session_state:
    st.session_state.devices = {
        f"Device_{i}": {
            "x": np.random.uniform(2, 8),
            "y": np.random.uniform(2, 8),
            "vlc_data": "",
        }
        for i in range(1, 6)
    }

# Sidebar: Device List
st.sidebar.header("📋 Devices on LAN")
for device_name in st.session_state.devices:
    st.sidebar.write(f"✅ {device_name}")

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📍 Device Positions (2D Space in Meters)")

    # Simulate position change
    for device in st.session_state.devices.values():
        device["x"] = np.clip(device["x"] + np.random.uniform(-0.1, 0.1), 0, 10)
        device["y"] = np.clip(device["y"] + np.random.uniform(-0.1, 0.1), 0, 10)

    # Prepare data
    device_data = pd.DataFrame([
        {"Name": name, "x": info["x"], "y": info["y"], "Type": "Device"}
        for name, info in st.session_state.devices.items()
    ])
    anchor_data = pd.DataFrame([
        {"Name": name, "x": info["x"], "y": info["y"], "Type": "Anchor"}
        for name, info in anchors.items()
    ])
    combined_data = pd.concat([device_data, anchor_data])

    # Plot
    chart = alt.Chart(combined_data).mark_circle(size=200).encode(
        x=alt.X("x", scale=alt.Scale(domain=[0, 10]), title="X (meters)"),
        y=alt.Y("y", scale=alt.Scale(domain=[0, 10]), title="Y (meters)"),
        color=alt.Color("Type", scale=alt.Scale(domain=["Device", "Anchor"], range=["steelblue", "orange"])),
        tooltip=["Name", "x", "y"]
    ).properties(width=600, height=600)
    st.altair_chart(chart, use_container_width=True)

    # Coordinates Table
    st.markdown("### 📊 Device Coordinates")
    st.dataframe(device_data[["Name", "x", "y"]].set_index("Name").round(2))

with col2:
    st.subheader("💡 VLC Communication Window")

    messages = []
    for name, info in st.session_state.devices.items():
        if np.random.rand() < 0.2:
            message = f"{name}: Hello via VLC at {time.strftime('%H:%M:%S')}"
            info["vlc_data"] = message
        if info["vlc_data"]:
            messages.append(info["vlc_data"])

    if messages:
        st.text_area("Received VLC Messages", value="\n".join(messages), height=300)
    else:
        st.info("No VLC messages received yet.")

