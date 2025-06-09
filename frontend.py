import streamlit as st
import pandas as pd
import numpy as np
import redis
import json
import altair as alt
from streamlit_autorefresh import st_autorefresh

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

st.set_page_config(page_title="LAN Device Tracker", layout="wide")
st.title("📡 LAN Device Tracker with VLC Monitor")

# Refresh every 5 seconds
st_autorefresh(interval=5000, key="auto_refresh")

# Read device positions from Redis
device_keys = r.keys("device:*")
devices = {
    key[7:]: json.loads(r.get(key))
    for key in device_keys
}

# Add placeholder VLC data
for name in devices:
    if f"vlc:{name}" not in st.session_state:
        st.session_state[f"vlc:{name}"] = ""

# Sidebar: Device List
st.sidebar.header("📋 Devices on LAN")
for name in devices:
    st.sidebar.write(f"✅ {name}")

# Fixed anchors
anchors = {
    "Anchor_1": {"x": 0, "y": 0},
    "Anchor_2": {"x": 10, "y": 0},
    "Anchor_3": {"x": 0, "y": 10},
    "Anchor_4": {"x": 10, "y": 10},
}

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📍 Device Positions (2D Space in Meters)")

    if devices:
        device_df = pd.DataFrame([
            {"Name": name, "x": info["x"], "y": info["y"], "Type": "Device"}
            for name, info in devices.items()
        ])
    else:
        st.warning("No devices found in Redis. Add some using the API.")
        device_df = pd.DataFrame(columns=["Name", "x", "y", "Type"])
    anchor_df = pd.DataFrame([
        {"Name": name, "x": info["x"], "y": info["y"], "Type": "Anchor"}
        for name, info in anchors.items()
    ])
    combined_df = pd.concat([device_df, anchor_df], ignore_index=True)

    chart = alt.Chart(combined_df).mark_circle(size=200).encode(
        x=alt.X("x", scale=alt.Scale(domain=[0, 10]), title="X (meters)"),
        y=alt.Y("y", scale=alt.Scale(domain=[0, 10]), title="Y (meters)"),
        color=alt.Color("Type", scale=alt.Scale(domain=["Device", "Anchor"], range=["steelblue", "orange"])),
        tooltip=["Name", "x", "y"]
    ).properties(width=600, height=600)

    st.altair_chart(chart, use_container_width=True)

    st.markdown("### 📊 Device Coordinates")
    if not device_df.empty:
        st.dataframe(device_df[["Name", "x", "y"]].set_index("Name").round(2))
    else:
        st.info("No device positions available yet.")

with col2:
    st.subheader("💡 VLC Communication Window")
    # Manual clear button
    if st.button("🧹 Clear All VLC Messages"):
        r.delete("vlc:messages")
        st.success("Cleared VLC messages")

    # Read messages (latest first)
    vlc_messages = r.lrange("vlc:messages", 0, 100)
    if vlc_messages:
        st.text_area("📥 Received VLC Messages", value="\n".join(vlc_messages), height=300)
    else:
        st.info("No VLC messages yet.")
