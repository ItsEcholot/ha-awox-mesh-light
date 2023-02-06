# ha-awox-mesh-light

Small script which uses the excellent [python-awox-mesh-light](https://github.com/Leiaz/python-awox-mesh-light) library by Leiaz and exposes a light entity to HomeAssistant using MQTT AutoDiscovery.

This has been developed for controlling a single AWOX lamp in its own BLE Mesh network.

Configuration is done through environment variables.

Dependencies needed (install them using pip):
- awoxmeshlight
- paho-mqtt

Usage example (all on a single line):
```
AWOX_MAC=A4:C1:38:xx:xx:xx AWOX_MESH_NAME=awox_mesh AWOX_MESH_PASSWORD=hunter2 MQTT_HOST=mqtt.local MQTT_USER=ha-awox-mesh-light MQTT_PASS=hunter2 python3 ha-awox-mesh-light/__init__.py
```

For a guide on how to set AWOX mesh name and password check the README on the [python-awox-mesh-light](https://github.com/Leiaz/python-awox-mesh-light) library.