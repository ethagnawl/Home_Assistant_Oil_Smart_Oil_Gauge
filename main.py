# /// script
# dependencies = [
#   "fastapi==0.116.1",
#   "uvicorn==0.35.0",
#   "python-dotenv==1.1.1",
#   "pyvirtualdisplay==3.0",
#   "paho-mqtt==2.1.0",
#   "selenium==4.11.0",
# ]
# requires-python = "==3.12"
# ///

import json
import paho.mqtt.publish as publish
import uvicorn

from datetime import datetime
from dotenv import dotenv_values, load_dotenv
from fastapi import FastAPI
from pprint import pprint
from pyvirtualdisplay import Display
from selenium import webdriver

load_dotenv()  

CONFIG = dotenv_values(".env")  
CONFIG["OIL_TANK_CAPACITY"] = float(CONFIG["OIL_TANK_CAPACITY"])

def main():
    display = Display(visible=0, size=(800, 600))
    display.start()

    browser = webdriver.Chrome()
    browser.set_window_size(1440, 900)
    browser.get(CONFIG["SMART_OIL_ENDPOINT"])

    browser.find_element("id", "inputUsername").send_keys(CONFIG["SMART_OIL_USERNAME"])
    browser.find_element("id", "inputPassword").send_keys(CONFIG["SMART_OIL_PASSWORD"])
    browser.find_element("class name", "btn").click()
    browser.implicitly_wait(5)



    nav = browser.find_element("xpath", '//p[contains(text(), "/")]').text

    fill_level = browser.find_element("xpath", "//div[@class='ts_col ts_level']//div[@class='ts_col_val']//p").get_attribute("innerHTML")
    fill_level = fill_level.split(r"/")
    current_fill_level = fill_level[0]
    current_fill_proportion = round((float(str(fill_level[0])) / float(str(fill_level[1]))) * 100, 1)
    battery_status = browser.find_element("xpath", "//div[@class='ts_col ts_battery']//div[@class='ts_col_val']//p").get_attribute("innerHTML")
    days_to_low = browser.find_element("xpath", "//div[@class='ts_col ts_days_to_low']//div[@class='ts_col_val']//p").get_attribute("innerHTML")

    nav_value = nav.split(r"/")
    browser.quit()

    results = {
            "battery_status": battery_status,
            "current_fill_level": current_fill_level,
            "current_fill_proportion": current_fill_proportion,
            "days_to_low": days_to_low,
    }

    pprint(f"{datetime.now()} - {results}")

    msgs = [{"topic": "oilgauge/tanklevel", "payload": json.dumps(results)}]
    publish.multiple(msgs, hostname=CONFIG["MQTT_HOSTNAME"], port=int(CONFIG["MQTT_PORT"]), auth={'username': CONFIG["MQTT_USERNAME"], 'password': CONFIG["MQTT_PASSWORD"]})

    display.stop()

    try:
        value = float(nav_value[0])
        percent_full = value/CONFIG["OIL_TANK_CAPACITY"] * 100
    except Exception as e:
        pprint(f"error: {str(e)}")
        percent_full = -1

    return {"value": percent_full}

app = FastAPI()

@app.get("/")
def read_root():
    return main()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(CONFIG["FAST_API_PORT"]))
