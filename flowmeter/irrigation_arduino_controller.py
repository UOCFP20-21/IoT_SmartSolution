"""
Script that contains mqtt connections, distribute mqtt orders to valve controller
and sends info-data received from flowmeter controller to mqtt broker server
"""
import json
import sys
import time
import datetime

import paho.mqtt.client as mqtt

from flowmeter import flowmeter_controller
from flowmeter.flowmeter_controller import get_flow, average
from flowmeter.valve_controller import order_to_switch

MQTTBroker = "192.168.1.100"
port = 1883
arduino_name = "RIEGO_SECTOR1_ARDUINO"
device_arduino = mqtt.Client(arduino_name)
sector = 1
# IoT system actions
client_topic = f"Sometimes/Riego/Sector{sector}"
# Admin received messages
admin_topic = f"Admin/Riego/Sector{sector}"
valve_topic = "/Valve"
flowmeter_topic = "/Flowmeter"
values_topic = "/Values"
error_topic = "/Error"
info_topic = "/Info"
# supposed water range. Only for debugging
water_flow = 25
valve_status = ""
min_flow_accepted = 1

warning_msg = ["No alerts", "Low water flow", "No water flow", "Flushing not stopped"]


def value_results_opened_valve(flow_media):
    global min_flow_accepted

    if flow_media > water_flow / 2:
        return 0
    elif flow_media > min_flow_accepted:
        return 1
    elif flow_media < min_flow_accepted:
        return 2
    return 0


def value_results_closed_valve(flow_media):
    global min_flow_accepted

    if flow_media > min_flow_accepted:
        return 3
    return 0


def value_results(medium_flow):
    if valve_status == "true":
        warning = value_results_opened_valve(medium_flow)
    else:
        warning = value_results_closed_valve(medium_flow)
    return warning


def send_warning(warning_code):
    global warning_msg

    if warning_code == 0:
        return
    else:
        device_arduino.publish(admin_topic + error_topic, warning_msg[warning_code])


def send_flow_realtime(flow):
    device_arduino.publish(admin_topic + flowmeter_topic, flow)


def send_valve_status(order):
    status_to_print = "Valve closed"
    if order == "true":
        status_to_print = "Valve Opened"
    print(f">> {status_to_print}")
    device_arduino.publish(admin_topic + valve_topic, status_to_print)


def get_info():
    global warning_msg, valve_status

    _status = False
    if valve_status == "true":
        _status = True

    flow = get_flow()
    medium_flow = average()
    warning = value_results(medium_flow)
    info_date = datetime.datetime.now().strftime("%A, %d, %b, %Y")
    info_time = datetime.datetime.now().strftime('%I:%M %S %p')

    info = {
        "sector": sector,
        "date": info_date,
        "time": info_time,
        "opened": _status,
        "average": medium_flow,
        "flow": flow,
        "warning": [
            {"code": warning,
             "message": warning_msg[warning]}
        ],
        "min_flow": min_flow_accepted
    }
    return json.dumps(info)


def send_info(info):
    device_arduino.publish(admin_topic + info_topic, info)


def set_values(value):
    global min_flow_accepted
    try:
        min_flow = value
        if min_flow > 0:
            min_flow_accepted = min_flow

    except Exception as not_parse:
        device_arduino.publish(admin_topic + error_topic, not_parse)


def received_topic(client, userdata, message):
    global valve_status
    order = message.payload.decode("utf-8")

    # flowmeter - values
    if message.topic == client_topic + flowmeter_topic + values_topic:
        values = json.loads(order)
        set_values(values)
        return

    # valve - switch on/off
    if message.topic == client_topic + valve_topic:
        valve_status = order_to_switch(order)

        send_valve_status(valve_status)
        return

    # info
    if message.topic == client_topic + info_topic:
        send_info(get_info())
        return


# noinspection PyBroadException
def connect_arduino():
    try:
        print(f"{arduino_name} > Connecting to {MQTTBroker} at port {port}...")
        device_arduino.connect(MQTTBroker, port)
        print(f"{arduino_name} > Connected!")
        device_arduino.subscribe(client_topic + "/#")
        print(f"{arduino_name} > Listening at '{client_topic}' topic")
        device_arduino.on_message = received_topic
        device_arduino.loop_forever()
    except Exception as ex:
        print(
            f"{arduino_name} Error >> Unable to connect to {MQTTBroker} at port {port} : {sys.exc_info()[0].__name__}")
