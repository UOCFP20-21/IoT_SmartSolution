import time

from flowmeter.flowmeter_controller import receiving_flow, set_flow_sim
from flowmeter.irrigation_arduino_controller import connect_arduino


def start_processes(process):
    if process == "arduino":
        connect_arduino()
    elif process == "physics":
        open_water_flow()
        for i in range(60):
            time.sleep(1)
            receiving_flow()


def open_water_flow(flow):
    set_flow_sim(flow)
    print("Current water flow is ", flow)


def close_water_flow():
    set_flow_sim(0)
    print("Current water flow is ", 0)


def test1_wf_on():
    print("TEST 1 | \n"
          " - Water flow open\n"
          " - valve open \n"
          " - flowmeter flushing water\n"
          " ----------------------------")

    connect_arduino()


# Application tester init function
if __name__ == '__main__':
    #close_water_flow()
    open_water_flow(25)
    test1_wf_on()
