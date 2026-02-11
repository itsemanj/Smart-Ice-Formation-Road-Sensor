
# Smart Ice Formation Road Sensor

A system to monitor road surface conditions for ice formation and store sensor data for analysis.

This project combines an **Arduino-based sensor device**, an **MQTT data pipeline**, and a **frontend dashboard** to detect, log, and visualize road conditions related to ice formation.

---

## Overview

Road icing is a major safety hazard in cold weather, causing reduced traction and increased accident risk for vehicles. This project implements a **smart road surface sensor** that:

- Monitors environmental conditions
- Publishes readings via MQTT
- Saves data into a local SQLite database
- Provides a frontend to view road condition data

The system is designed for easy deployment on roadside infrastructure and can be extended for vehicle warning systems or integration into larger road weather information systems (RWIS). ([ESA Commercialisation Gateway][1])

---

##  Repository Structure

```
/
├── arduino/                 # Arduino sensor firmware
├── frontend/                # Web UI to visualize sensor data
├── mqtt_to_sqlite.py        # Bridge script: MQTT → SQLite
├── sensor_data.db           # Sample database (optional)
├── .gitignore
```

---

##  Components

###  Arduino Sensor

The `arduino/` folder contains firmware code that reads sensor data (e.g., temperature, humidity) and publishes it over MQTT.

Typical features:

* Road surface temperature monitoring
* Environmental condition sensing
* MQTT publishing for real-time telemetry

 *You may need to modify sensor pin definitions and MQTT credentials for your environment.*

---

###  MQTT to SQLite Bridge

The `mqtt_to_sqlite.py` script subscribes to the MQTT broker for sensor topics and writes the incoming data into a local SQLite database `sensor_data.db`.

Basic features:

* Connects to a specified MQTT broker
* Parses JSON sensor payloads
* Inserts timestamped readings into a local database

**Usage:**

```bash
python3 mqtt_to_sqlite.py --broker <BROKER_HOST> --topic <TOPIC>
```

---

###  Frontend Dashboard

The `frontend/` folder hosts a dashboard to visualize logged sensor data, typically showing:

* Time-series temperature plots
* Ice formation risk indicators
* Historical condition graphs

You can serve this locally (e.g., with a simple HTTP server) or integrate with a backend API.

---

##  Installation

Make sure you have:

* Python 3.7+
* MQTT broker (e.g., Mosquitto)
* Arduino IDE (for firmware)
* Web server (for frontend)

### 1. Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run MQTT to SQLite Bridge

```bash
python mqtt_to_sqlite.py
```

### 3. Run Frontend

Serve the `frontend` directory:

```bash
cd frontend
python3 -m http.server 8000
```

---

## Development

* Use consistent topic names and JSON payload schemas between Arduino and Python bridge
* Add authentication to MQTT for security
* Enhance the frontend with realtime charts using libraries like Chart.js or D3.js

---

## Deployment

This system can be deployed on embedded devices (e.g., Raspberry Pi or edge nodes). Ice detection sensors are commonly part of smart road systems for winter safety. ([ESA Commercialisation Gateway][1])


