#!/bin/bash
# --- Setup openvswitch ---

source ./config.sh

# Delete the bridge if it has already been created.
sudo ovs-vsctl --if-exists del-br $openvswitch_bridge_name 2>/dev/null
# Create the bridge
sudo ovs-vsctl add-br $openvswitch_bridge_name

for device_name in ${device_names[@]}; do
    # For all devices other than self
    if [ $self_name != $device_name ]; then
        port=${devices[${self_name}_id]}${devices[${device_name}_id]}
        # Setup a connection with a given port.
        sudo ovs-vsctl add-port $openvswitch_bridge_name p_$port -- set interface p_$port type=vxlan options:remote_ip=${devices[${device_name}_ip]} options:key=100 ofport_request=${devices[${self_name}${device_name}_port]}
    fi
done

# Set the controller ip address
sudo ovs-vsctl set-controller $openvswitch_bridge_name tcp:${controller_ip}:6653

# Set protocol
sudo ovs-vsctl set bridge $openvswitch_bridge_name protocols=OpenFlow13 stp_enable=true

# --- Setup probe network VM on configured openvswitch ---

sudo ovs-vsctl del-port $openvswitch_bridge_name probe
sudo ovs-vsctl add-port $openvswitch_bridge_name probe -- set Interface probe type=internal ofport_request=1

sudo ip addr add dev probe $probe_CIDR
sudo ip link set dev probe mtu 1400 up

# Check output
sudo ovs-vsctl show
