# Intro Links

Batman:
[https://www.open-mesh.org/projects/open-mesh](https://www.open-mesh.org/projects/open-mesh)
[https://witestlab.poly.edu/blog/batman/](https://witestlab.poly.edu/blog/batman/)

Openflow and SDN
[https://opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.5.1.pdf](https://opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.5.1.pdf)
[https://ieeexplore.ieee.org/document/7473831](https://ieeexplore.ieee.org/document/7473831)

Openflow+Batman:
[https://ieeexplore.ieee.org/document/6866608](https://ieeexplore.ieee.org/document/6866608)

Uses BATMAN as a mesh routing protocol instead of something like (Optimized Link State Routing) OLSR. Chosen because BATMAN can operate at layer 2 instead of layer 3. BATMAN was used to "identify nexthop nodes, maintain node topology, and provide local mesh topology knowledge when establishing data paths. The Internet gateways in the mesh network provide global mesh topology information through an API to a remote server."


#TODO finish this
[https://dl.acm.org/doi/10.1145/3293614.3293616](https://dl.acm.org/doi/10.1145/3293614.3293616)

Hieu: you can also read this survey to understand wireless SDN: [https://ieeexplore.ieee.org/document/7473831](https://ieeexplore.ieee.org/document/7473831)

# Protocol
[overview](https://www.open-mesh.org/projects/open-mesh/wiki/BATMANConcept)
[Draft rfc](https://datatracker.ietf.org/doc/html/draft-wunderlich-openmesh-manet-routing-00)

Updated [Protocol information](<https://www.open-mesh.org/projects/batman-adv/wiki/Protocol_information>)
## BATMAN IV

Detailed explanation on OGM messages and improvements vs V3 [here](https://www.open-mesh.org/projects/batman-adv/wiki/BATMAN_IV)

[Originator Messages (OGM)](https://www.open-mesh.org/projects/batman-adv/wiki/OGM)

All nodes broadcast originator messages to neighbors.
### [OGMv1](https://www.open-mesh.org/projects/batman-adv/wiki/OGM)

- Consist of
    - Originator address: Node that creates message
    - Sender address: Last node to rebroadcast OGM message
    - TTL (Time to live)
    - Sequence Number: Increases in time to allow for chronological ordering of new messages.

## BATMAN V

changes from IV [here](https://www.open-mesh.org/projects/batman-adv/wiki/BATMAN_V)

B.A.T.M.A.N. V adopts the strategy of 'divide & conquer' to handle these different uses cases better: For neighbor discovery the [Echo Location Protocol (ELP)](https://www.open-mesh.org/projects/batman-adv/wiki/ELP) is introduced. This packet type is never forwarded or rebroadcasted in the mesh. The [Originator Messages version 2 (OGMv2)](https://www.open-mesh.org/projects/batman-adv/wiki/OGMv2) protocol remains responsible for flooding the mesh with link quality information and determining the overall path transmit qualities.

#TODO if only looking for batman to determine neighbor values set the ogm rebroadcast timing to a very big number to only utilize ELP

 Quality is chosen based upon a [throughput metric](https://www.open-mesh.org/projects/batman-adv/wiki/BATMAN_V#Throughput-based-metric) as defined here. Basically just average estimate of bits/sec towards a neighbor.
### [The Originator Message 2 (OGMv2) Format:](https://www.open-mesh.org/projects/batman-adv/wiki/Ogmv2)

- Packet type: Initialize this field with the ELP packet type.
- Version: Set your internal compatibility version.
- TTL: Initialize with BATADV_TTL
- Flags: not used
- Sequence number: On first broadcast set the sequence number to an arbitrary value and increment the field by one for each following OGMv2.
- Originator Address: Set this field to the primary MAC address of this B.A.T.M.A.N. node.
- TVLV length: Length of the TLVL data appended to the OGM
- Throughput: Throughput metric value in 100 kbit/s. Initialize with BATADV_THROUGHPUT_MAX_VALUE
- TVLV data: Appended TVLV data for the originator. See [TVLV](https://www.open-mesh.org/projects/batman-adv/wiki/TVLV) for a detailed description.

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Packet Type   |    Version    |      TTL      |   Flags       |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                       Sequence Number                         |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                     Originator Address                        |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |  (cont'd) Originator Address  |  TVLV length                  |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                         Throughput                            |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                        TVLV data ...                          |
```

Nodes rebroadcast messages they receive and keep track of originator addresses they receive in an [originator table](https://www.open-mesh.org/projects/batman-adv/wiki/Understand-your-batman-adv-network)

This table can be used to route messages to non-adjacent peers by checking transmit quality (TQ) levels of known connections through neighbors.

This table can also be [used](https://www.open-mesh.org/projects/batman-adv/wiki/Understand-your-batman-adv-network#translation-tables) with external mac-address to attach non-batman nodes to the network.

It can [also](https://www.open-mesh.org/projects/batman-adv/wiki/Understand-your-batman-adv-network#Distributed-ARP-Table-local-cache-table) used to proxy with the internet.

Filtering is done on incoming ogm messages to only listen to originators from the currently chosen best.
### [The Echo Location Protocol (ELP) Format:](https://www.open-mesh.org/projects/batman-adv/wiki/ELP)

- Packet type: Initialize this field with the ELP packet type.
- Version: Set your internal compatibility version.
- TTL: not used.
- Num Neigh: The number of neighbors that this neighbour already discovered with the interface where this packet was sent.
- Sequence number: On first broadcast set the sequence number to an arbitrary value and increment the field by one for each following broadcast.
- Interval: Set to the current ELP interval of this interface in milliseconds. The default interval is 500ms and it may be reconfigured during run-time.
- Originator Address: Set this field to the primary MAC address of this B.A.T.M.A.N. node.

If this B.A.T.M.A.N. interface wants to announce neighboring nodes it should append a neighbor entry message for each neighbor to be announced and fill the "number of neighbors" field accordingly.


```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Packet Type   |    Version    |      TTL      |   Num Neigh   |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                       Sequence Number                         |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                          Interval                             |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                     Originator Address                        |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |      Originator Address       |                               |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Quality now based on a factor of throughout / echo Quality

# Batman-adv
Works on layer 2 (mac addresses) instead of 3 (ip addresses). The daemon acts on layer 3

Lots of algorithm tweaks [here](https://www.open-mesh.org/projects/batman-adv/wiki/Tweaking#routing-algorithm) such as logging, multicast, ogm rebroadcast interval (default 1 sec), etc.

[Here](https://patchwork.open-mesh.org/project/b.a.t.m.a.n./list/) is a list of feature patches

Sends data payloads with ethernet frames as described [here](https://www.kernel.org/doc/html/latest/networking/batman-adv.html#batman-adv)

manpage: <https://downloads.open-mesh.org/batman/manpages/batctl.8.html>

overview for adv: <https://www.open-mesh.org/projects/batman-adv/wiki/Doc-overview>

## Batman Installation
Kernal must be $\ge$ Debian 2021.4 for json output. Currently using debian-2023.0-1 [batman-adv: 2022.3] on Pi. This version can output in JSON. No need to write a parser.
```
sudo apt update -y
sudo apt upgrade -y
sudo apt install batctl bridge-utils -y
sudo modprobe batman-adv
sudo batctl -v
```
#### Testing
```
sudo batctl if add eth0
sudo batctl meshif bat0 nj
```
#### Batman Script for Rasp 4
Original [Reddit Article](https://www.reddit.com/r/darknetplan/comments/68s6jp/how_to_configure_batmanadv_on_the_raspberry_pi_3/)
##### Make sure that the wifi is disabled
* Make a script called batsetup.sh.
* sudo chmod +x batsetup.sh
* [./batsetup.sh](../Scripts/batsetup.sh)

You have to make sure all the AP's are the same. It should be the cell ID you see when calling iwconfig. If not, use this command:
```
sudo iwconfig wlan0 ap <AP id>
```

Checking the network:
```
route -n

# ipv6 of wlan0 should match other pi's
sudo batctl o
```

checking controlled interfaces: `batctl if`

# Reading State in Python
To read the neighbor table use [[json.py]]

To install on the pi's:
1. Make a virtual environment
```bash
mkdir <venv_dir>
python3 -m venv <venv_dir>
```
2. Install [json-parser](https://pypi.org/project/json-parser/)
```
<venv_dir>/bin/pip3 install json-parser
```
3. Run the script
```
<venv_dir>/bin/python3 json.py
```

To get other information from the other batman commands, modify the command in the script (e.g. `nj` becomes `oj` for the originators table).

*Note* that the `data` variable returned from parsing can be indexed like `data['value']`
