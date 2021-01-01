"""
Script that listen flowmeter actions and sends data to
"""
from random import randrange

flow = 0
start_range = 0
readings = []
flow_received = 0

name = "SECTOR1_FLOWMETER"

def clear_readings():
    global readings

    readings = []


def average():
    total_received = 0
    for f in readings:
        total_received += f
    return total_received / len(readings)


def set_flow_sim(in_flow):
    global flow, start_range

    flow = in_flow
    if in_flow != 0:
        start_range = int(in_flow / 2)
        print(f"({start_range} > {flow}")

# this function is supposed to be active when arduino ask flowmeter
def receiving_flow():
    global flow

    read_flow = randrange(start_range, flow)
    print(f"{name} : Flow received > {read_flow}")
    return read_flow


def get_flow():

    _flow = receiving_flow()
    readings.append(_flow)
    return _flow
