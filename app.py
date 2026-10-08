from flask import Flask, render_template, jsonify, make_response
import paho.mqtt.client as mqtt
import json
import threading
from datetime import datetime

app = Flask(__name__)

# ==================================================
# MQTT SETTINGS
# ==================================================

MQTT_BROKER = "10.52.179.37"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/temperature"

# ==================================================
# SENSOR DATA
# ==================================================

sensor_data = {
    "temperature": 0.0,
    "relay": "OFF",
    "warning": "WAITING FOR DATA",
    "mqtt_connected": False,
    "last_update": "--"
}

# ==================================================
# MQTT CONNECT
# ==================================================

def on_connect(client, userdata, flags, rc):

    print("MQTT CONNECT RESULT:", rc)

    if rc == 0:

        sensor_data["mqtt_connected"] = True

        print("==============================")
        print("MQTT CONNECTED")
        print("BROKER:", MQTT_BROKER)
        print("TOPIC:", MQTT_TOPIC)
        print("==============================")

        client.subscribe(MQTT_TOPIC)

        print("SUBSCRIBED TO:", MQTT_TOPIC)

    else:

        sensor_data["mqtt_connected"] = False

        print("MQTT CONNECTION FAILED:", rc)


# ==================================================
# MQTT MESSAGE
# ==================================================

def on_message(client, userdata, msg):

    try:

        message = msg.payload.decode("utf-8")

        print("MQTT MESSAGE RECEIVED:")
        print(message)

        data = json.loads(message)

        temperature = float(data["temperature"])
        relay = str(data["relay"])

        sensor_data["temperature"] = temperature
        sensor_data["relay"] = relay

        if temperature > 30:

            sensor_data["warning"] = "HIGH TEMPERATURE"

        else:

            sensor_data["warning"] = "NORMAL"

        sensor_data["last_update"] = datetime.now().strftime("%H:%M:%S")

        print("UPDATED SENSOR DATA:")
        print(sensor_data)
        print("--------------------------------")


    except Exception as e:

        print("MQTT DATA ERROR:", e)


# ==================================================
# MQTT DISCONNECT
# ==================================================

def on_disconnect(client, userdata, rc):

    sensor_data["mqtt_connected"] = False

    print("MQTT DISCONNECTED")


# ==================================================
# MQTT CLIENT
# ==================================================

mqtt_client = mqtt.Client(
    client_id="Flask_Dashboard"
)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect


# ==================================================
# MQTT THREAD
# ==================================================

def mqtt_thread():

    try:

        print("Connecting Flask to MQTT broker...")

        mqtt_client.connect(
            MQTT_BROKER,
            MQTT_PORT,
            60
        )

        mqtt_client.loop_forever()

    except Exception as e:

        print("MQTT ERROR:", e)


threading.Thread(
    target=mqtt_thread,
    daemon=True
).start()


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/")
def dashboard():

    print("================================")
    print("DASHBOARD PAGE REQUESTED")
    print("Template folder:", app.template_folder)
    print("================================")

    response = make_response(
        render_template("dashboard.html")
    )

    # Disable browser caching
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# ==================================================
# API
# ==================================================

@app.route("/api/data")
def get_data():

    print("================================")
    print("API REQUEST RECEIVED")
    print("DATA:", sensor_data)
    print("================================")

    response = jsonify(sensor_data)

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"

    return response


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    print("================================")
    print("FLASK IoT DASHBOARD")
    print("================================")
    print("Dashboard: http://127.0.0.1:5000")
    print("API:       http://127.0.0.1:5000/api/data")
    print("MQTT:      ", MQTT_BROKER)
    print("Topic:     ", MQTT_TOPIC)
    print("================================")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )