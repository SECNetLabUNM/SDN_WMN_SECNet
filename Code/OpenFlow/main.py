import sys
import requests
import json

from totalSwitches import OVSSwitches
from pushFlows import PushFlow

allSwitch = PushFlow()
def ping_node1_node3():
    br0ID = allSwitch.GetBridgeID(0)
    allSwitch.PushSwitch(br0ID, 0, 2, 1, "50.50.50.1", "50.50.50.2", 10)
    allSwitch.PushSwitch(br0ID, 0, 2, 10, "50.50.50.2", "50.50.50.1", 1)
    # allSwitch.GetFlowStats(0)

    br1ID = allSwitch.GetBridgeID(1)
    allSwitch.PushSwitch(br1ID, 0, 2, 1, "50.50.50.2", "50.50.50.1", 10)
    allSwitch.PushSwitch(br1ID, 0, 2, 10, "50.50.50.1", "50.50.50.2", 1)
    # allSwitch.GetFlowStats(1)
def ping_node1_node2():
    br0ID = allSwitch.GetBridgeID(0)
    allSwitch.PushSwitch(br0ID, 0, 2, 1, "50.50.50.1", "50.50.50.2", 10)
    allSwitch.PushSwitch(br0ID, 0, 2, 10, "50.50.50.2", "50.50.50.1", 1)
    # allSwitch.GetFlowStats(0)

    br1ID = allSwitch.GetBridgeID(1)
    allSwitch.PushSwitch(br1ID, 0, 2, 1, "50.50.50.2", "50.50.50.1", 10)
    allSwitch.PushSwitch(br1ID, 0, 2, 10, "50.50.50.1", "50.50.50.2", 1)
    # allSwitch.GetFlowStats(1)

def node2_setup():
    br1ID = allSwitch.GetBridgeID(1)
    allSwitch.PushSwitch(br1ID, 0, 2, 20, "50.50.50.3", "50.50.50.1", 10)
    allSwitch.PushSwitch(br1ID, 0, 2, 10, "50.50.50.1", "50.50.50.3", 20)


def runner():
    #allSwitch.GetBridgeAll(0)
    #allSwitch.GetBridgeAll(1)
    #allSwitch.GetBridgeAll(2)
    node2_setup()

if __name__ == "__main__":
    #runner()
    total = OVSSwitches()
    print(total.ReturnSwitches())
    #os.system("rm *.txt")
