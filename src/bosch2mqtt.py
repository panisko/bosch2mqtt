""" Test script of bosch_thermostat_client. """
import asyncio
import logging
import os
import json
import datetime

import aiohttp
import time
import paho.mqtt.client as mqtt
import bosch_thermostat_client as bosch
from bosch_thermostat_client.const.ivt import IVT
from bosch_thermostat_client.const import HC, DHW, TYPE, RECORDINGS, HTTP

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

mblan_token = os.environ.get("MBLAN_ACCESS_KEY")
mblan_password = os.environ.get("MBLAN_PASSWORD")
mblan_ip = os.environ.get("MBLAN_IP")
mqtt_host = os.environ.get("MQTT_IP")
mqtt_port = os.environ.get("MQTT_PORT")
sleep = int(os.environ.get("MBLAN_SLEEP"))



client = mqtt.Client(clean_session=True, transport="tcp")
client.connect(host="192.168.70.100", port=1883, keepalive=60)
client.loop_start()


exclude_list = ['Pool temperature', 'Hotwater temp', 'Switch temp']


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


async def main():
    async with aiohttp.ClientSession() as session:
        bosch_gateway = bosch.gateway_chooser(device_type=IVT)
        gateway = bosch_gateway(
            session=session,
            session_type=HTTP,
            host=mblan_ip,
            access_token=mblan_token,
            password=mblan_password,
        )
        await gateway.check_connection()
        sensors = await gateway.initialize_sensors()
        while True:
            now = datetime.datetime.timestamp(datetime.datetime.now())
            for sensor in sensors:
                if str(sensor.kind) == 'regular':
                    topic = str(sensor.name.replace(" ", "/")).lower()
                    if sensor.name in exclude_list:
                        continue
                    # print(str(sensor.name))
                    await sensor.update()
                    value = sensor.state
                    if value == "on":
                        value = 1
                    if value == "off":
                        value = 0
                    if isinstance(value, float):

                        # print("topic: " + topic)
                        dict = {
                            "time" : now,
                            "value": value
                        }

                        client.publish("mblan/"+topic, payload=json.dumps(dict), qos=0, retain=False)
            time.sleep(sleep)
        # await gateway.initialize_circuits(HC)
        # await session.close()


asyncio.get_event_loop().run_until_complete(main())
