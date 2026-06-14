# Disconnect Guard

Simple utility for Lineage 2 that monitors the disconnect message and performs an action when detected.

## Features

- Detects disconnect popup using image recognition
- Works across multiple monitors
- Runs in the system tray
- Optional PC shutdown after disconnect detection
- Portable executable support

## Requirements

```bash
pip install -r requirements.txt
```

## Run

```bash
python l2watch.py
```

## Build

```bash
pyinstaller --onefile --noconsole --name DisconnectGuard --add-data "disconnect.png;." l2watch.py
```
