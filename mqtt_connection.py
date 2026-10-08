from flask import Flask, jsonify, render_template
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Store latest distance
latest_distance = 0.0

MQTT_BROKER = "10.52.179.37"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/ultrasonic/distance"


# MQTT connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC)
        print("Subscribed to:", MQTT_TOPIC)
    else:
        print("MQTT connection failed:", rc)


# Receive data from ESP8266
def on_message(client, userdata, msg):
    global latest_distance

    try:
        latest_distance = float(msg.payload.decode())

        print("Distance received:",
              latest_distance, "cm")

    except ValueError:
        print("Invalid data received")


# Create MQTT client
mqtt_client = mqtt.Client()

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start MQTT in background
mqtt_client.loop_start()


@app.route("/")
def home():
    return f"""
    <html>
        <head>
            <title>Ultrasonic Distance</title>
        </head>

        <body>
            <h1>ESP8266 Ultrasonic Sensor</h1>

            <h2>
                Distance:
                {latest_distance} cm
            </h2>

            <meta http-equiv="refresh" content="2">

        </body>
    </html>
    """


@app.route("/distance")
def distance():
    return jsonify({
        "distance_cm": latest_distance
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )