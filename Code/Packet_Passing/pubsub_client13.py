import socket as sck
import json
import random
import time
import subprocess
import requests

def get_local_ip():
    try:
        # Create a temporary socket to an external address (e.g., Google's public DNS server)
        # This doesn't establish a connection, so the target address can be almost anything
        s = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS server IP and port
        local_ip = s.getsockname()[0]  # Get the socket's own address
        s.close()
    except Exception as e:
        print(f"Error: {e}")
        local_ip = "Unable to determine local IP"
    return local_ip

server_ADDR = "100.100.1.5"
server_PORT = 9559
# IMPORTANT: set the NIC that B.A.T.M.A.N is using here
nic_name = "wlan0"

def gen_random_number(flr, ceil):
    return random.randint(flr, ceil)

class ClientHandler:
    def __init__(self, addr, port):
        self._ADDR = addr
        self._Port = port
        self._mac = self.retrieve_client_MAC()
        self._ip = self.retrieve_client_IP()
        self.device_id = self.retrieve_client_ID()
        # This is the main dictionary packet
        self.device_info = {
            "ID": self.device_id,
            "MAC": self._mac,
            "IP": self._ip,
            "Neighbor_Tuple": [False],
            "XYZ_Tuple": [False]
        }

    def retrieve_client_IP(self):
        try:
            output = subprocess.run(["ifconfig", "bat0"],
                                    capture_output=True,
                                    text=True)
            text_output = output.stdout.strip()
            IP = ""

            for line in text_output.split("\n"):
                if line.lstrip().startswith("inet"):
                    elements = line.split()
                    if len(elements) >= 2:
                        IP = elements[1]
                        break
            return IP

        except Exception as e:
            print(f"Error trying to get the IP: {e}")
            return None

    def retrieve_client_MAC(self):
        try:
            output = subprocess.run(["ifconfig", nic_name],
                                    capture_output=True,
                                    text=True)
            text_output = output.stdout.strip()
            mac = ""

            for line in text_output.split("\n"):
                if line.lstrip().startswith("ether"):
                    elements = line.split()
                    if len(elements) >= 2:
                        mac = elements[1]
                        break
            return mac

        except Exception as e:
            print(f"Error trying to get the MAC: {e}")
            return None

    def retrieve_client_ID(self):
        br = ""

        try:
            output = subprocess.run(["sudo", "ovs-vsctl", "show"],
                                    capture_output=True,
                                    text=True)

            text_output = output.stdout.strip()

            for line in text_output.split("\n"):
                if line.lstrip().startswith("Bridge"):
                    elements = line.split()
                    if len(elements) >= 1:
                        br = elements[1]
                        break
        except Exception as e:
            print(f"Error in getting the bridge: {e}")

        # input dummy entry for mac
        command = f"sudo ovs-ofctl -O OpenFlow13 add-flow {br} 'table=99, priority=0, ip, dl_src={self._mac}, actions=drop'"
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to add flow: {str(e)}")

        # retrieve list of switch ID's
        get_switches = f'http://{server_ADDR}:8080/stats/switches'
        respond_switches = requests.get(get_switches)
        switches = respond_switches.json()

        switchID = 0

        # search the list of ID's for the mac
        for sw in switches:
            url = f'http://{server_ADDR}:8080/stats/flow/{sw}'
            response = requests.get(url)

            flows = response.json()
            switch_id = list(flows.keys())[0]
            for flow in flows[switch_id]:
                if flow['table_id'] == 99:
                    match = flow.get('match', {})
                    dl_src = match.get('dl_src')
                    if dl_src and dl_src == self._mac:
                        switchID = switch_id
                        break

        return switchID

    def retrieve_client_neighbors(self):
        try:
            output = subprocess.run(["sudo", "batctl", "o"],
                                    capture_output=True,
                                    text=True)
            text_output = output.stdout.strip()
            neigh_mac = []
            neigh_LQ = []

            for line in text_output.split("\n"):
                if line.lstrip().startswith("*"):
                    elements = line.split()

                    if len(elements) >= 5:
                        current_location = elements[1]
                        if elements[3] == '(':
                            link_quality = elements[4].strip(")")
                            next_hop = elements[5]
                        else:
                            link_quality = elements[3].strip("()")
                            next_hop = elements[4]
                        if link_quality:
                            # If the next hop is the same as the current, no need
                            # to put the next hop
                            if current_location == next_hop:
                                neigh_mac.append(current_location)
                            # Else add the next hop
                            else:
                                print("else")
                                neigh_mac.append([current_location, next_hop])

                            neigh_LQ.append(link_quality)

            return neigh_mac, neigh_LQ

        except Exception as e:
            print(f"Error trying to get BAT info: {e}")
            return None

    def return_device_neighbors(self):
        Mac, LQ = self.retrieve_client_neighbors()

        device_neighbors = {
            "nMAC": Mac,
            "LQ": LQ
        }

        return device_neighbors

    def make_device(self, subbed_info, subbed_xyz):
        if subbed_info:
            device_neighbors = self.return_device_neighbors()
            self.device_info["Neighbor_Tuple"] = [True, device_neighbors]
        else:
            self.device_info["Neighbor_Tuple"] = [False]

        if subbed_xyz:
            device_xyz = {
                "x": gen_random_number(0, 999),
                "y": gen_random_number(0, 999),
                "z": gen_random_number(0, 999)
            }
            self.device_info["XYZ_Tuple"] = [True, device_xyz]
        else:
            self.device_info["XYZ_Tuple"] = [False]

    def connection(self):
        first_connection = True
        client_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        while True:
            try:
                client_socket.connect((self._ADDR, self._Port))
                while True:
                    if first_connection:
                        first_connection = False
                    else:
                        data = client_socket.recv(1024)
                        if data:
                            conditions = json.loads(data.decode('utf-8'))
                            print(f"From server! {conditions}")
                            condition_neighbors = conditions["Req_Neigh"]
                            condition_XYZ = conditions["Req_XYZ"]
                            self.make_device(condition_neighbors, condition_XYZ)

                    # TODO: Optimize this to make it only send the TUPLES. The other datas should be static
                    # TODO: do not troll and try to actually do this
                    print(f"To server:\n{self.device_info}")
                    json_data = json.dumps(self.device_info)
                    client_socket.sendall(json_data.encode('utf-8'))

                    time.sleep(2)

            except sck.error:
                print(f"Error: {sck.error}")
                print(f"Retrying to connect to server: {self._ADDR}")
                client_socket.close()
                time.sleep(5)

if __name__ == "__main__":
    client = ClientHandler(server_ADDR, server_PORT)
    client.connection()
