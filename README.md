# VLCP_frontend

A simple frontend for Visible light positioning and visible light communication network.

Based on python streamlit framework.

## Feature

- Show online VLP anchors and positioning targets in LAN.
- Display VLP results in a dynamic scatter plot.
- Show VLC data in plain text.
- Support display VLC BER in real time.

## Installation

For debian system:

`docker run -p 6379:6379 redis`

`pip install streamlit fastapi uvicorn redis`

## Run

To start the frontend, run:

`streamlit run frontend.py`

To start the backend, run:

`uvicorn backend:app --reload --port 8000`
