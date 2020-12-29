"""
Script that listen flowmeter actions and sends data to
"""
from random import randrange, randint

flow = 0
start_range = 0

name = "SECTOR1_FLOWMETER"

def set_flow_sim(nflow):
    global flow, start_range
    flow = nflow
    if nflow != 0:
        start_range = nflow/2


# this function is supposed to be active when arduino ask flowmeter
def receiving_flow():
    global flow
    rflow = randint(start_range, flow)
    if rflow == 0:
        return rflow
    print(f"{name} : Flow received > {rflow}")
    return rflow



