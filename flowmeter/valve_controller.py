"""
Script that controls solenoid valve actions
"""
from flowmeter.flowmeter_controller import clear_readings

switch_name = "SECTOR1_SWITCH"
valve_name = "SECTOR1_VALVE"

def open_close_valve(order):
    # we would place the logic of valve device.
    # will return true or false depends of the result of the proces and if it has been finalized
    return order


def order_to_switch(order):

    if order == "true":
        print(f"{switch_name} : order sent > Open valve")
    else:
        clear_readings()
        print(f"{switch_name} : order sent > Close valve")
    return open_close_valve(order)
