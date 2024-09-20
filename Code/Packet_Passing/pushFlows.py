import requests
from totalSwitches import OVSSwitches

class PushFlow(OVSSwitches):
    def __init__(self):
        super().__init__()
        self._add_url = "http://localhost:8080/stats/flowentry/add"
        self._sw = self.ReturnSwitches()
        self._priority = 0

    def GetBridgeName(self, index):
        currentID = str(self._sw[index])
        output = requests.get(f"http://localhost:8080/"
                              f"stats/portdesc/"
                              f"{currentID}")
        port_desc = output.json()
        bridge = port_desc[currentID][0]['name']
        return bridge

    def GetBridgeMAC(self, index):
        currentID = str(self._sw[index])
        output = requests.get(f"http://localhost:8080/"
                              f"stats/portdesc/"
                              f"{currentID}")
        port_desc = output.json()
        MAC = port_desc[currentID][0]['hw_addr']
        return MAC

    def GetBridgeAll(self, index):
        currentID = str(self._sw[index])
        output = requests.get(f"http://localhost:8080/"
                              f"stats/portdesc/"
                              f"{currentID}")
        port_desc = output.json()
        bridge = port_desc[currentID]
        return bridge


    def GetBridgeID(self, index):
        currentID = str(self._sw[index])
        return currentID

    def PushSwitch(self, bridgeID, table_id, priority, in_port, ipv4_src, ipv4_dst, out_port):
        flow_entry = {
            "dpid": bridgeID,
            "table_id": table_id,
            "cookie": 0,
            "cookie_mask": 0,
            "priority": priority,
            "match": {
                "in_port": in_port,
                "eth_type": 2048,
                "nw_src": str(ipv4_src),
                "nw_dst": str(ipv4_dst),
            },
            "actions": [
                {
                    "port": out_port,
                    "type": "OUTPUT"
                }
            ]
        }
        response = requests.post(self._add_url, json=flow_entry)
        if response.status_code == 200:
            print(f"Flow entry successfully pushed to {bridgeID}")
        else:
            print("Failed")
            print(f"{response.content}")

    def GetFlowStats(self, index):
        currentID = str(self._sw[index])
        output = requests.get(f"http://localhost:8080/"
                              f"stats/flow/"
                              f"{currentID}")
        port_desc = output.json()
        bridge = port_desc[currentID]
        print(bridge)

    def DeleteAllEntries(self, index):
        dpid = self.GetBridgeID(index)
        del_url = f"http://localhost:8080/stats/flowentry/clear/{dpid}"
        response = requests.delete(del_url)
        if response.status_code == 200:
            print(f"Flow entries cleared successfully from {dpid}")
        else:
            print(f"Failed to clear flow entries from {dpid}")
