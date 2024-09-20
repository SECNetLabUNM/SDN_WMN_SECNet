# Information

# Links

OpenVSwitch Manual:
[https://www.openvswitch.org//support/dist-docs/ovs-ofctl.8.txt](https://www.openvswitch.org//support/dist-docs/ovs-ofctl.8.txt)

OpenFlow Compatibility:
[https://docs.openvswitch.org/en/latest/faq/openflow/](https://docs.openvswitch.org/en/latest/faq/openflow/)

OVS with SDN:
[https://medium.com/@blackvvine/sdn-part-2-building-an-sdn-playground-on-the-cloud-using-open-vswitch-and-opendaylight-a0e2de029ce1](https://medium.com/@blackvvine/sdn-part-2-building-an-sdn-playground-on-the-cloud-using-open-vswitch-and-opendaylight-a0e2de029ce1)
# Commands

#### Installation
```
sudo apt install openvswitch-switch
```

#### Show All OpenVSwitch Options
```
sudo ovs-vsctl show
```

#### Create Bridge
```
sudo ovs-vsctl add-br <br_x>
```

#### Create Port (VTEP)
```
sudo ovs-vsctl add-port <br_x> <port_x> -- set Interface <port_x> type=[type] options:remote_ip=<remote_ip> options:keys=flow
```
##### \[type\]
* internal: inside of the switch.
* vxlan: vlan connect, complication ethernet. Needs remote IP.
* gre: generic routing encapsulation, general purpose tunnel. Needs remote IP.

You can set the interface individually without add-port:
```
sudo ovs-vsctl set Interface <port_x> type=[type] options:remote_ip=<remote_ip> options:keys=flow
```

#### Connect to Controller
```
sudo ovs-vsctl set-controller <br_x> tcp:<controller_ip>:<port>
```

#### IP Adding Shenanigans
This is for if you want to create a test port within the switch. You must create an internal port within the switch. type=internal, no remote_ip.
```
sudo ovs-vsctl add-br <br_x> <int_port> -- set Interface <int_port> type=internal
```

```
sudo ip addr add 192.168.1.1/24 dev <int_port>
sudo ifconfig <int_port> 192.168.1.1 netmask 255.255.255.0 up
route -n
```

#### Set Bridge Protocols
```
# Please check OVS version compatibility before doing all OpenFlow versions. At minimum, it should do OpenFlow13
sudo ovs-vsctl set bridge br_x protocols=OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14
```

#### Deletion
```
sudo ovs-vsctl del-br <br_x>
sudo ovs-vsctl del-port <br_x> <port_x>
```

#### Flushing Routing Table
```
sudo ip route flush table main
sudo reboot
```

### FULL SCRIPT
[./openvswitch_setup.sh](../Scripts/openvswitch_setup.sh)
#### Explanation
- (x,y are custom number per device e.g. 1, 2)
- `br_x` is the name of the switch being setup. For example `br_1`
- `p_xy` is the port from x to y e.g. `p_12` to go from pi1 to 2
- `<ip of br_y>` refers to the wireless ip used to reach the other device. If using batman it is the batman assigned ip. If using a wireless access point it would the ip assigned by the access point. e.g. `192.168.1.45` (not `192.168.1.45/24`)
- options:key=100 assigns the id 100 to the network that `br_x` is going to be part of
- ofport_request=10 uses port 10 to communicate with the other device. Both sides of the connection should use the same port but different ports for each other device.
- `stp_enable=true` enables the [spanning tree protocol](https://en.wikipedia.org/wiki/Spanning_Tree_Protocol) because layer 2 networks don't support [switching loops](https://en.wikipedia.org/wiki/Switching_loop)
  - the port states (blocked, forwarding, etc) can be viewed with `sudo ovs-appctl stp/show`

#### Connecting Host to Bridge

OpenVSwitch is designed to connect virtual machines together across networks. It acts as an overlay switch/network. What we do is create a switch that will connect the VM or for this case, a simple tap port, to itself and establish a vxlan connection to the pi across the network.

What VxLAN does is that it map's the tap port's ip with the underlying network ip, then it encapsulates the tap port's packets with the underlying network, essentially making that packet an underlying network packet. For this case, the underlying network will be B.A.T.M.A.N. The packet will be pushed to the other side where it exits the destination's VTEP, gets de-capsulated, then pushed up to the destination tap port.

![](images/vxlan_encap.png)

[Image Source](https://medium.com/@blackvvine/sdn-part-2-building-an-sdn-playground-on-the-cloud-using-open-vswitch-and-opendaylight-a0e2de029ce1)
#### Topology Diagram

```
  Node 1 * {br_1} ------- (Port:10) ------- Node 2 * {br_2}
[Probe: 50.50.50.1]                       [Probe: 50.50.50.2]
[Bat0: 100.100.1.1]                       [Bat0: 100.100.1.2]
         |                                         |
         |                                         |
         |                                         |
     (Port:40)                                 (Port:20)
         |                                         |
         |                                         |
         |                                         |
  Node 4 * {br_4} ------- (Port:30) ------- Node 3 * {br_3}
[Probe: 50.50.50.4]                       [Probe: 50.50.50.3]
[Bat0: 100.100.1.4]                       [Bat0: 100.100.1.3]

Controller (OpenFlow13)
[Bat0: 100.100.1.5]
```
# OpenFlow Shenanigans
You will need to use this command to print OpenFlow descriptions based on the manual.
```
sudo ovs-ofctl -O OpenFlowV <setting> br_x
```
* OpenFlowV = OpenFlow versions, ie OpenFlow13
* \<setting\> are the settings provided by the manpage for [`ovs-ofctl`](https://manpages.debian.org/testing/openvswitch-common/ovs-ofctl.8.en.html) with fields at manpage for [`ovs-fields`](https://manpages.debian.org/testing/openvswitch-common/ovs-fields.7.en.html)
  * may need `--strict` to use `ovs-ofctl del-flows` on some fields like `priority`
* br_x is the controller / bridge

#### Flow Entry
```
// ---- This one is the output flow ---- //
table=0,priority=1,in_port=1,ip,nw_src=50.50.50.1,nw_dst=50.50.50.2,actions=output:10
// ---- This one is the input flow ---- //
table=0,priority=1,in_port=10,ip,nw_src=50.50.50.2,nw_dst=50.50.50.1,actions=output:1
// ---- This one is for the controller ---- //
table=0,priority=0,actions=CONTROLLER:65535
```

10 is your vtep (p_21 as an example) port. 1 is your probe port.