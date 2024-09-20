import requests
import json

class OVSSwitches:
    def __init__(self):
        self.all_switches = []
        self.InitSwitches()

    def InitSwitches(self):
        output = requests.get("http://localhost:8080/stats/switches")
        self.all_switches = output.json()

    def ReturnSwitches(self):
        return self.all_switches

    def RetNSwitch(self, n):
        return self.all_switches[n]

    def OverWriteSwitches(self, switch):
        self.all_switches = switch