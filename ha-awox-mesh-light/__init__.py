#!/usr/bin/env python3

import os
import sys
import random
import time
import math
import json
import awoxmeshlight
import paho.mqtt.client as mqtt

BASE_TOPIC = "homeassistant/light/awox-mesh-light"

light = awoxmeshlight.AwoxMeshLight(os.getenv('AWOX_MAC'), os.getenv('AWOX_MESH_NAME'), os.getenv('AWOX_MESH_PASSWORD'))
light.connectWithRetry(num_tries=3)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    print("Publishing Auto Discovery message")
    publish_availability('online')
    publish_state()
    publish_ha_discovery()
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("{}/set".format(BASE_TOPIC))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    if msg.topic == "{}/set".format(BASE_TOPIC):
        body = json.loads(msg.payload)
        if "state" in body:
            if body["state"] == 'ON' and not light.status:
                light.on()
            elif body["state"] == 'OFF' and light.status:
                light.off()
            time.sleep(0.120)

        if "brightness" in body:
            target_white_brightness = math.floor((body["brightness"] / 255) * 0x7f)
            if light.white_brightness != target_white_brightness:
                light.setWhiteBrightness(target_white_brightness)
                time.sleep(0.120)
        
        if "color_temp" in body:
            target_color_temp = math.floor(mapFromTo(body["color_temp"], 153, 370, 0, 0x7f))
            if light.white_temp != target_color_temp:
                light.setWhiteTemperature(target_color_temp)
                time.sleep(0.120)

        if "color" in body:
            colors = body["color"]
            if light.red != colors["r"] or light.green != colors["g"] or colors["b"]:
                light.setColor(colors["r"], colors["g"], colors["b"])
                time.sleep(0.120)
    
    publish_state()

def publish_ha_discovery():
    topic = "{}/config".format(BASE_TOPIC)
    client.publish(topic, payload=json.dumps({
        "schema": "json",
        "name": "ha-awox-mesh-light",
        "unique_id": light.mac,
        "brightness": True,
        "color_mode": True,
        "brightness_scale": 255,
        "supported_color_modes": ["color_temp", "rgb"],
        "device": {
            "model": light.getModelNumber().decode("utf-8"),
            "name": light.getModelNumber().decode("utf-8"),
            "sw_version": light.getFirmwareRevision().decode("utf-8"),
            "manufacturer": "Eglo",
            "identifiers": light.mac
        },
        "min_mirs": 153,
        "max_mirs": 370,
        "retain": True,
        "availability_topic": "{}/availability".format(BASE_TOPIC),
        "state_topic": "{}/state".format(BASE_TOPIC),
        "command_topic": "{}/set".format(BASE_TOPIC)
    }), retain=True)

def publish_availability(availability):
    client.publish("{}/availability".format(BASE_TOPIC), payload=availability, retain=True)

def publish_state():
    light.readStatus()
    time.sleep(0.120)
    topic = "{}/state".format(BASE_TOPIC)
    client.publish(topic, payload=json.dumps({
        "state": "ON" if light.status else "OFF",
        "brightness": (light.white_brightness / 0x7f) * 255,
        "color_mode": "color_temp" if light.mode in [1,5] else "rgb",
        "color_temp": mapFromTo(light.white_temp, 0, 0x7f, 153, 370),
        "color": {
            "r": light.red,
            "g": light.green,
            "b": light.blue
        }
    }), retain=True)

def mapFromTo(x,a,b,c,d):
   y=(x-a)/(b-a)*(d-c)+c
   return y

client = mqtt.Client(client_id="ha-awox-mesh-light", clean_session=False)
client.on_connect = on_connect
client.on_message = on_message
client.will_set("{}/availability".format(BASE_TOPIC), payload='offline', retain=True)

client.username_pw_set(os.getenv('MQTT_USER'), password=os.getenv('MQTT_PASS'))
client.connect(os.getenv('MQTT_HOST'), 1883, 60)
client.loop_forever()