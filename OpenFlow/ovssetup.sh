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
