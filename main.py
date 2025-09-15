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

import paho.mqtt.publish as publish
import uvicorn

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
    nav_value = nav.split(r"/")
    browser.quit()
    pprint(f"values: {nav_value[0]}")
    publish.single("oilgauge/tanklevel", nav_value[0], hostname=CONFIG["MQTT_HOSTNAME"], port=int(CONFIG["MQTT_PORT"]), auth={'username': CONFIG["MQTT_USERNAME"], 'password': CONFIG["MQTT_PASSWORD"]})

    display.stop()

    try:
        value = float(nav_value[0])
        percent_full = value/CONFIG["OIL_TANK_CAPACITY"] * 100
    except Exception as e:
        print(f"error: {str(e)}")
        percent_full = -1

    return {"value": percent_full}

app = FastAPI()

@app.get("/")
def read_root():
    return main()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(CONFIG["FAST_API_PORT"]))
