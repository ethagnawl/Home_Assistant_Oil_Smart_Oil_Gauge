# Smart Oil Gauge in Home Assistant
Web scraper for the Smart Oil Gauge to bring data into Home Assistant. This simple solution scrapes the Smart Oil Gauge website and sends a captured value via MQTT to a Home Assistant sensor.

This is a "modern" fork of https://github.com/marecotec/Home_Assistant_Oil_Smart_Oil_Gauge. That project is not licensed, so this project is provided as-is and I am not responsible for whatever you may do with it. 

This is still very much WIP.

### Dependencies
1. Home Assistant
2. MQTT server 
3. Smart Oil Gauge sensor
4. UV
5. Customized .env file

#### .env
Copy .env.sample to .env (.gitignored) and enter _your_ environmental information.

### Architecture
#### FastAPI server
Exposes an HTTP route whose handler runs the oil gague scraping code, publishes an MQTT message with the reading and returns data to caller. My main.py script is a riff on oil.py but I would like to include some of the more sophisticated readings available in oil_multiple.py. Also, there is no authentication mechanism in place, so don't expose this to the world as it could potentially be abused. 

The script is run by UV which is responsible for managing the specified Python and package dependencies. I'm being lazy and manually running it inside a tmux pane but a more durable approach would be to create a systemd service which gracefully handles restarts, logging, etc.

The script is invoked with: `uv run main.py`


#### Home Assistant sensors
##### MQTT
This is a modified version of the upstream repo's MQTT config which adheres to HA's new configuration.yaml schema:

```
mqtt:
  - sensor:
      name: "Oil level"
      state_topic: "oilgauge/tanklevel"
      unique_id: "smart_oil_level_mqtt_gallons"
      unit_of_measurement: "gallons"
      value_template: '{{value_json.current_fill_level}}'

  - sensor:
      state_topic: "oilgauge/tanklevel"
      value_template: '{{value_json.current_fill_proportion}}'
      unit_of_measurement: "%"
      name: "Oil level percent"
      unique_id: "smart_oil_level_mqtt_percent"

  - sensor:
      state_topic: "oilgauge/tanklevel"
      value_template: '{{value_json.battery_status}}'
      name: "Oil level battery"
      unique_id: "smart_oil_level_mqtt_battery_level"

  - sensor:
      state_topic: "oilgauge/tanklevel"
      value_template: '{{value_json.days_to_low}}'
      unit_of_measurement: "days"
      name: "Oil level days to low"
      unique_id: "smart_oil_level_mqtt_days_to_low"
```

##### CLI
The provided Home Assistant config snippet runs a shell script (see main.sh) every N seconds to fetch data from server. It's important to note that I'm running Home Assistant inside a Docker container and the FastAPI server on its host. _For me_, this workflow is simpler than trying to shoehorn the Python dependency chain _and_ the headless browser into the HA container, although that could probably be done. (I think HA now includes UV and this project's Python script is (mostly) self-contained, so this could be worth exploring further but the browser component sounds like a pain.)

```
command_line:
  sensor:
      name: Smart Oil Level
      unique_id: smart_oil_level
      command: "echo -e $(/config/scripts/smart-oil-level/main.sh)"
      command_timeout: 120
      scan_interval: 300
```


<img width="509" height="789" alt="Screenshot from 2025-09-16 11-53-47-crop" src="https://github.com/user-attachments/assets/5c6af3cf-3e0d-4164-a912-cfb54b4acbed" />
