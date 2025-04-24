# Pub/Sub GUI Instructions
This graphical user interface, `PubSubGUI.py`, is used for requesting or subscribing data from each OpenvSwitch host. To provide data, there is client code called `PubSubClient13.py` that must run on each OpenvSwitch host. It will be implemented as a client-server approach where the GUI will act as the centralized server and should be ran on the same device as the RYU controller device. 

## PubSubClient13.py
The client code is ran on each OpenvSwitch device. For our test bed, each Raspberry Pi will be running this code. It will require python's `requests` to be installed. It should already be available in the requirements in the [OpenFlow folder](../OpenFlow/OpenFlow_Instructions.md) but here is the download command if you want to install independently. 
```
pip install requests 
```

This code also requires the Rest API to be enabled controller side otherwise it will not be able to request some features.

It is recommended to run this code after setting up BATMAN and the OpenvSwitches on your devices:
```
python3 PubSubClient13.py
```

### Request Data
The client will provide the GUI with the following data dictionary from the device:

1. OpenFlow switch ID 
2. Device MAC address
3. Device IP address
4. Neighbor tuple
5. XYZ tuple

The first three should be self explanatory with the switch ID coming from the RYU server itself. 

The neighbor tuple contains the following, a request boolean condition indicating the request status from the GUI, and the Batman IV transmission quality (TQ), aka, the link quality between each BATMAN device. Since multi-hop routing is enabled, we can also request the TQ between the host and its multi-hop neighbors. The TQ calculations are done by the Batman IV algorithm which is broken down here:

[https://www.open-mesh.org/projects/batman-adv/wiki/BATMAN_IV](https://www.open-mesh.org/projects/batman-adv/wiki/BATMAN_IV)

The client simply requests the TQ by using the `sudo batctl o` command and taking the row with the asterisks or the most ideal hops and TQ level determined by Batman IV.  We will only take the originator, the TQ itself which is from [0,255], and the next hop. Even though the originator and next hop are in MACs, we can still map them with the host switch ID and IPs on the GUI side. A neighbor tuple can look like this:

`[True, {Originator, LQ, Next Hop}]`

The XYZ tuple contains the following, a request boolean condition indicating the request status from the GUI, and the host location. Because this project will eventually be deployed on a network of drones, it is vital to have drone location data for each host. However since each hosts are Raspberry Pis, we must simulate their location by randomizing each euclidean coordinate from [0,999]. A XYZ tuple can look like this:

`[True, {X, Y, Z}]`

To help mitigate traffic, the data dictionary will be sent one way from the client to the GUI. The GUI will send a request tuple to the client indicating what tuple it wants to request from the individual client. This tuple will look like this, `[False, False]`. The first element is the neighbor tuple request status, and the second is the XYZ tuple request status. If either are true, the client will update the tuples from the data dictionary with the latest information. This tuple is the GUI to client communication while the booleans in the neighbor and xyz tuples are more for the GUI back end itself.

## PubSubGUI.py
This GUI code is ran on only one device which we recommend to be the same as the one hosting the RYU controller. It is built using custom tkinter which should be in the requirements.txt in the [OpenFlow folder](../OpenFlow/OpenFlow_Instructions.md) but can be installed manually via this command:
```
pip install customtkinter
```

To run the GUI, use this:
```
python3 PubSubGUI.py
```

The GUI will be activated like so:

![Diagram](images/GUI_start.png)


At the start, the GUI will always have one host, which will be the computer hosting the GUI itself. Because this computer is still a BATMAN enabled host, we should still be able to retrieve its TQ information and its location data. This is what the GUI looks like with no other OpenvSwitch device running `PubSubClient13.py`.

