# Pub/Sub GUI Instructions
This graphical user interface, `PubSubGUI.py`, is used for requesting or subscribing data from each OpenvSwitch host. To provide data, there is client code called `PubSubClient13.py` that must run on each OpenvSwitch host.

## PubSubClient13.py
The client code is ran on each OpenvSwitch device. For our test bed, each Raspberry Pi will be running this code. It will require python's `requests` to be installed using 
```
pip install requests 
```

