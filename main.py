import streamlit as st
import pandas as pd
import numpy as np
import time
import socket
import threading

st.set_page_config(layout="wide")
st.title("VLCP monitor system")

# Simulated data store
device_list = []
device_positions = {}
vlc_messages = {}
bit_error_rate_log = []

# Mutex for thread-safe updates
from threading import Lock
data_lock = Lock()

# Simulate LAN scan (replace with actual scan logic in real use)
def simulate_lan_devices():
    with data_lock:
        device_list.clear()
        for i in range(5):
            ip = f"192.168.1.{100 + i}"
            device_list.append(ip)
            device_positions[ip] = np.random.rand(2) * 10
            vlc_messages[ip] = f"Init Msg from {ip}"
            bit_error_rate_log.append((time.time(), np.random.rand() * 0.05))

# Simulate real-time update of positions and communication
def update_device_data():
    while True:
        time.sleep(1)
        with data_lock:
            for ip in device_list:
                # Random movement
                device_positions[ip] += (np.random.rand(2) - 0.5) * 0.5
                device_positions[ip] = np.clip(device_positions[ip], 0, 10)

                # Update VLC message
                vlc_messages[ip] = f"VLC Msg from {ip} at {time.strftime('%H:%M:%S')}"

                # Update BER
                ber = np.random.rand() * 0.05
                bit_error_rate_log.append((time.time(), ber))
                if len(bit_error_rate_log) > 100:
                    bit_error_rate_log.pop(0)

# Start background simulation thread
threading.Thread(target=update_device_data, daemon=True).start()
simulate_lan_devices()

# Layout
col1, col2 = st.columns([1, 2])
col3, col4 = st.columns([1, 1])

# Display device list
with col1:
    st.subheader("Devices on LAN")
    with data_lock:
        for ip in device_list:
            st.text(ip)

# Scatter plot
with col2:
    st.subheader("Device Positions")
    placeholder = st.empty()

# VLC message box
with col3:
    st.subheader("VLC Communication Log")
    vlc_text = st.empty()

# BER line graph
with col4:
    st.subheader("Bit Error Rate (BER)")
    ber_chart = st.empty()

# Real-time updating loop
while True:
    time.sleep(1)
    with data_lock:
        # Update scatter plot
        df = pd.DataFrame({
            'x': [pos[0] for pos in device_positions.values()],
            'y': [pos[1] for pos in device_positions.values()],
            'ip': list(device_positions.keys())
        })
        # fig = px.scatter(df, x='x', y='y', text='ip', range_x=[0, 10], range_y=[0, 10], title="Device Positions")
        # fig.update_traces(textposition='top center')
        placeholder.write(df, use_container_width=True)

        # Update VLC text
        text_log = "\n".join([f"{ip}: {msg}" for ip, msg in vlc_messages.items()])
        vlc_text.text_area("VLC Data", text_log, height=300)

        # Update BER line graph
        times, bers = zip(*bit_error_rate_log) if bit_error_rate_log else ([], [])
        ber_df = pd.DataFrame({'Time': times, 'BER': bers})
        ber_chart.line_chart(ber_df.set_index('Time'))


