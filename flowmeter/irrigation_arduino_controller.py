"""
Script that contains mqtt connections, distribute mqtt orders to valve controller
and sends info-data received from flowmeter controller to mqtt broker server
"""
import json
import sys
import time
import datetime

import paho.mqtt.client as mqtt
from flowmeter import flowmeter_controller, valve_controller

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
read_flow_seconds = 10
min_flow_accepted = 1
warning_msg = ["", "Low water flow", "No water flow", "Flushing not stopped"]


def media(flow_received):
    sum = 0
    for f in flow_received:
        sum += f
    return sum / len(flow_received)


def value_results_opened_valve(flow_media):
    if flow_media > water_flow / 2:
        return 0
    elif flow_media > min_flow_accepted:
        return 1
    elif flow_media < min_flow_accepted:
        return 2


def value_results_closed_valve(flow_media):
    if flow_media > min_flow_accepted:
        return 3


def value_results(flow_media):
    if valve_controller.status == "true":
        warning = value_results_opened_valve(flow_media)
    else:
        warning = value_results_closed_valve(flow_media)
    return warning


def send_warning(warning_code):
    global warning_msg
    if warning_code == 0:
        return
    else:
        device_arduino.publish(admin_topic + error_topic, warning_msg[warning_code])


def send_flow_media(flow_media):
    device_arduino.publish(admin_topic + flowmeter_topic, flow_media)
    send_warning(value_results(flow_media))


def send_flow_realtime(flow):
    device_arduino.publish(admin_topic + flowmeter_topic, flow)


def get_flow():
    global min_flow_accepted
    flow_received = []

    for i in range(read_flow_seconds):
        flow = flowmeter_controller.receiving_flow()
        flow_received.append(flow)

    return media(flow_received)


def send_valve_status(order):
    status_to_print = "Valve closed"
    if order == "true":
        status_to_print = "Valve Opened"
    print(f">> {status_to_print}")
    device_arduino.publish(admin_topic + valve_topic, status_to_print)
    time.sleep(5)
    flow_obtained = get_flow()
    send_flow_realtime(flow_obtained)
    send_flow_media(flow_obtained)


def get_info():
    global warning_msg, min_flow_accepted, read_flow_seconds

    status = False
    if valve_controller.status == "true":
        status = True

    flow = get_flow()
    result = value_results(flow)
    info_date = datetime.datetime.now().strftime("%A, %d, %b, %Y")
    info_time = datetime.datetime.now().strftime('%I:%M %S %p')

    info = {
        "sector": sector,
        "date": info_date,
        "time": info_time,
        "opened": status,
        "flow": flow,
        "warning": [
            {"code": result,
             "message": warning_msg[result]}
        ],
        "min_flow": min_flow_accepted,
        "seconds_read": read_flow_seconds
    }
    return json.dumps(info)

def send_info(info):
    device_arduino.publish(admin_topic + info_topic, info)


def set_values(values):
    global read_flow_seconds, \
        min_flow_accepted
    try:
        min_flow = int(values["min_flow"])
        seconds_read = int(values["seconds_read"])

        if seconds_read > 0:
            read_flow_seconds = seconds_read
        if min_flow > 0:
            min_flow_accepted = min_flow
    except Exception as not_parse:
        device_arduino.publish(admin_topic + error_topic, not_parse)

def received_topic(client, userdata, message):
    order = message.payload.decode("utf-8")
    if message.topic == client_topic + flowmeter_topic + values_topic:
        values = json.loads(order)
        set_values(values)
        return

    if order == "info":
        send_info(get_info())
        return

    valve_controller.order_to_switch(order)
    send_valve_status(valve_controller.status)


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
    except Exception:
        print(
            f"{arduino_name} Error >> Unable to connect to {MQTTBroker} at port {port} : {sys.exc_info()[0].__name__}")
