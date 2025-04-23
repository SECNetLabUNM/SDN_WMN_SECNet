# Pub/Sub GUI Instructions
This graphical user interface, `PubSubGUI.py`, is used for requesting or subscribing data from each OpenvSwitch host. To provide data, there is client code called `PubSubClient13.py` that must run on each OpenvSwitch host. It will be implemented as a client-server approach where the GUI will act as the centralized server and should be ran on the same device as the RYU controller device. 

## PubSubClient13.py
The client code is ran on each OpenvSwitch device. For our test bed, each Raspberry Pi will be running this code. It will require python's `requests` to be installed. It should already be available in the requirements in the OpenFlow section but here is the download command if you want to install independently. 
```
pip install requests 
```

This code also requires the Rest API to be enabled controller side otherwise it will not be able to request some features.

To run this, simply do:
```
python3 PubSubClient13.py
```

### Request Data
The client will provide the GUI with the following data from the device:
1. OpenFlow switch ID 
2. Device MAC address
3. Device IP address
4. Neighbor tuple
5. XYZ tuple
