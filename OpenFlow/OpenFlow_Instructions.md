## Controller Installation
We ran the RYU SDN controller on our most powerful device with the best NIC available. We recommend you do the same.

To run the controller, the minimum requirement we have found is `python 3.8.10` and `pip 20.0.2`. These are the python and pip3 versions we are using. Please create an environment that can run this python version. Below is our dependencies that are required for both the RYU controller.

```
setuptools==44.0.0
eventlet==0.30.2
certifi==2023.7.22
charset-normalizer==3.3.0
debtcollector==2.5.0
dnspython==1.16.0
eventlet==0.31.1
greenlet==3.0.0
idna==3.4
msgpack==1.0.7
netaddr==0.9.0
oslo.config==9.2.0
oslo.i18n==6.1.0
ovs==3.1.2
packaging==20.9
pbr==5.11.1
pyparsing==3.1.1
PyYAML==6.0.1
repoze.lru==0.7
requests==2.31.0
rfc3986==2.0.0
Routes==2.5.1
six==1.16.0
sortedcontainers==2.4.0
stevedore==5.1.0
tinyrpc==1.0.4
urllib3==2.0.6
WebOb==1.8.7
wrapt==1.15.0
```
With these dependencies installed, the RYU controller can be installed by running:

`pip install ryu`

Next, you must download the RYU GitHub provided below. 

[https://github.com/faucetsdn/ryu](https://github.com/faucetsdn/ryu)

If you want to download RYU from the GitHub, switch to this directory where you can either try the `setup.py` file or try `cd ryu; pip install .`. Note RYU is discontinued and the installation process can be frustrating. If there are any weird errors, the issues section of the RYU GitHub might provide some answers.

To confirm that RYU is working, move to the `/ryu/app` section and run `ryu-manager simple_switch_13.py`. We recommend only running `ryu-manager` within the RYU git folder itself. If there are no error messages, the controller is working. This will run a controller that is OpenFlow 1.3 enabled. Note, you can run multiple programs at once with different flags that you will see later on.

### RYU Upgraded GUI
Provided is a GitHub to an upgraded GUI that runs with the RYU controller. We recommend using this GUI as we use it within our implementation.

[https://github.com/martimy/flowmanager](https://github.com/martimy/flowmanager)

This GUI requires `eventlet==0.30.2` and RYU to be installed and running. To run this GUI, run this command.

```
ryu-manager --observe-links ~/flowmanager/flowmanager.py ~/ryu/ryu/app/simple_switch_13
```

We have only tested this GUI with OpenFlow 1.3. Anomalies might occur with other OpenFlow versions. 

The GUI is web based and can be located through this link: [http://localhost:8080/home/index.html](http://localhost:8080/home/index.html)
### Enable Rest API
We highly recommend enabling the Rest API as the pub/sub gui will not work without it. Here is the command to enable it:

```
ryu-manager ~/ryu/ryu/app/simple_switch_13 ~/ryu/ryu/app/ofctl_rest.py
```

### Enable Upgraded GUI and Rest API

```
ryu-manager --observe-links ~/flowmanager/flowmanager.py ~/ryu/ryu/app/simple_switch_13 ~/ryu/ryu/app/ofctl_rest.py
```
## OpenvSwitch Installation
The official OpenvSwitch can be found here:

[https://docs.openvswitch.org/en/latest/](https://docs.openvswitch.org/en/latest/)

We ran our OpenvSwitches on our Raspberry Pis. To install OpenvSwitch, use the following command:
```
sudo apt install openvswitch-switch
```

To check if it is installed, use this command:
```
sudo ovs-vsctl show
```

This command shows all the active switches known as bridges. Since it is a fresh install, there will be no bridge here.

### OvS Script
```
# 1. Create bridge / switch name
sudo ovs-vsctl del-br br_$NUM$
sudo ovs-vsctl add-br br_$NUM$

# 2. VXLAN to Neighbors
sudo ovs-vsctl add-port br_$NUM$ $PORT_NAME$ -- set interface $PORT_NAME$ type=VXLAN options:remote_ip=$NEIGHBOR_IP$ ofport_request=$PORT_NUM$

# 3. Controller Connection
sudo ovs-vsctl set-controller br_$NUM$ tcp:$CTRL_IP$:6653

sudo ovs-vsctl set-controller br_$NUM$ connection-mode=in-band

# 4. OpenFlow Version
sudo ovs-vsctl set bridge br_$NUM$ protocols=OpenFlow13

# 5. Internal port
sudo ovs-vsctl add-port br_$NUM$ probe -- set interface probe type=internal ofport_request=$PORT_INT$
sudo ip addr add $PROBE_IP$/24 dev probe
sudo ifconfig probe $PROBE_IP$/24 mtu 1400 up

# 6. Confirm
sudo ovs-vsctl show
```

1. This section creates the switch. We recommend to name your bridge br_0 or any other number tat you would like if you are running multiple switches. `del-br` is to delete any possible switch with the same name and `add-br` adds a switch.
2. This section is for creating a port and connection to another switch. Note this is for switch to switch connection only. `$PORT_NAME` is the name of the port. `$NEIGHBOR_IP` is the IP that you want this switch to connect to. Note this is NOT the same as the BATMAN IP.  You will use an entirely different IP for the virtual switches. `$PORT_NUM$` is the number for this port. It is recommended to choose one as it is easier to keep up on what switch to connected to where.
3. This section is to create a link to the controller. `$CTRL_IP$` is the IP of the controller.
4. This section is to make sure the OvS is using OpenFlow 1.3
5. This section is to create the pseudo virtual machine in the form of an internal port. This port is a dummy and does nothing except act as a pseudo host device connected to the switch. `$PORT_INT$` will be your internal port number. We recommend something like 1 to keep it simple. `$PROBE_IP$` will be the IP of these dummy probes. These IPs will also be the IP you will be using to connect the virtual switches in section 2. We recommend making these IPs very different from the BATMAN ones.
6. Confirmation to show that all commands are working. OpenvSwitch will print out the switch and its settings.

If there are any errors, we recommend deleting the bridge and retrying the script. A device restart is recommended to clear any IP addresses used by the switch however the switch must be deleted first. 

### OvS Commands
#### ovs-vsctl
There are two types of OpenvSwitch commands that we use. The most common one is the `ovs-vsctl` command that acts as a creation tool. A full list of all this command can do can be found here:

[https://www.openvswitch.org/support/dist-docs/ovs-vsctl.8.txt](https://www.openvswitch.org/support/dist-docs/ovs-vsctl.8.txt)

All sitch creation and modification commands that we use will be started with:
```
sudo ovs-vsctl 
```

To create a virtual switch, otherwise known as a bridge, the `add-br` command is needed followed by the name of the bridge, usually called `br_#`. Deletion of the bridge would be `del-br`, followed by the name of the bridge. Here is an example:
```
sudo ovs-vsctl add-br br_0
sudo ovs-vsctl del-br br_0
```

With the creation of a virtual switch, you can now add virtual ports. The command `add-port`, followed by the bridge name and the port name will be used:
```
sudo ovs-vsctl add-port br_$NUM$ $PORT_NAME$
```
However, we do not doing recommend creating the probes alone without any additional features as our OvS tried to look for a network device with the same name. We recommend fully completing your port with all of its features with the `set interface` command. 

You first need to set a `type` for the port. This can be `internal` which means a dummy port, or `VXLAN` which is the encapsulation protocol that will require a `remote_ip` or a destination. Type `internal` will not require a destination. Optionally, you can also add a port number to your port. We recommend doing this. 
```
sudo ovs-vsctl add-port br_$NUM$ $PORT_NAME$ -- set interface $PORT_NAME$ type=VXLAN options:remote_ip=$NEIGHBOR_IP$ ofport_request=$PORT_NUM$
```

```
sudo ovs-vsctl add-port br_$NUM$ probe -- set interface probe type=internal ofport_request=$PORT_INT$
```
Example:
```
sudo ovs-vsctl add-port br_0 port_01 -- set interface port_01 type=VXLAN options:remote_ip=192.168.1.1 ofport_request=10
```

```
sudo ovs-vsctl add-port br_0 probe -- set interface probe type=internal ofport_request=1
```

Note, for internal ports like this probe, you will need to give it an IP and enable it using your ifconfig. You need to make it available to the network. 

#### ovs-ofctl
We use `ovs-ofctl` as a switch end command to manually input and retrieve flow entries. This command is very useful for experimentation on the switch end. The full list of this command can be found here:

[https://www.openvswitch.org//support/dist-docs/ovs-ofctl.8.txt](https://www.openvswitch.org//support/dist-docs/ovs-ofctl.8.txt)

To check a flow entry, use this command:
```
sudo ovs-ofctl -O OpenFlow$OF_Version$ dump-flows br_$NUM$
```
Example:
```
sudo ovs-ofctl -O OpenFlow13 dump-flows br_0
```

You must specify the OpenFlow version such as 13 for 1.3 with a `-O` flag preceding it. `dump-flows` is the command to dump data plane entries. 

