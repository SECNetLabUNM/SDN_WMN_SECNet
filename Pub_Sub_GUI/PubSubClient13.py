import socket as sck
import json
import random
import time
import subprocess
import requests

# TODO: you need to modify these values to your host device BATMAN addr and NIC
server_ADDR = "100.100.1.5"
server_PORT = 9559
# IMPORTANT: set the NIC that B.A.T.M.A.N is using here
nic_name = "wlp2s0"

# This function is used to create random numbers using a floor and ceiling
def gen_random_number(flr, ceil):
    return random.randint(flr, ceil)

# This is the main class responsible for hosting the client.
# Its methods are divided into separate parts that allows it to extract information
# for different metric of the host device. It will be divided into parts and sub parts.
class ClientHandler:
    # Part I.A: Default constructor, this is where the main
    # data dictionary is stored.
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

    # Part I.B: This method is used to taking the BATMAN
    # IP from the host device.
    def retrieve_client_IP(self):
        try:
            # Executing the command to retrieve the IP
            output = subprocess.run(["ifconfig", "bat0"],
                                    capture_output=True,
                                    text=True)
            # Output to string
            text_output = output.stdout.strip()
            IP = ""

            # Splits all lines into elements
            for line in text_output.split("\n"):
                # Start from the line that says inet
                if line.lstrip().startswith("inet"):
                    # Divide all words into an array
                    elements = line.split()
                    if len(elements) >= 2:
                        # The IP should be the first element after inet
                        IP = elements[1]
                        break
            return IP

        # Otherwise throw exception
        except Exception as e:
            print(f"Error trying to get the IP: {e}")
            return None

    # Part I.C: This method is used for retrieving the MAC address
    # of the host device.
    def retrieve_client_MAC(self):
        try:
            # Executing the command to retrieve the MAC
            output = subprocess.run(["ifconfig", nic_name],
                                    capture_output=True,
                                    text=True)
            # Output to string
            text_output = output.stdout.strip()
            mac = ""

            # Splits all lines into elements
            for line in text_output.split("\n"):
                # Start from the line that says ether
                if line.lstrip().startswith("ether"):
                    # Divide all words into an array
                    elements = line.split()
                    if len(elements) >= 2:
                        # The MAC should be the first element after ether
                        mac = elements[1]
                        break
            return mac

        # Otherwise throw exception
        except Exception as e:
            print(f"Error trying to get the MAC: {e}")
            return None

    # Part I.D: This method is used to retrieve the switch ID. It utilized the REST API.
    # NOTE: the controller must already be running in order for this method to work
    def retrieve_client_ID(self):
        br = ""

        # This is used to retrieve the name of the bridge. It
        # will not matter what you renamed it as. However, this ONLY
        # works iff there is only ONE bridge/virtually switch. Please
        # be careful and make sure only one bridge is active
        try:

            # Executing the command to retrieve the bridge name
            output = subprocess.run(["sudo", "ovs-vsctl", "show"],
                                    capture_output=True,
                                    text=True)

            # Output to string
            text_output = output.stdout.strip()

            # Splits all lines into elements
            for line in text_output.split("\n"):
                # Start from the line that says Bridge
                if line.lstrip().startswith("Bridge"):
                    # Divide all words into an array
                    elements = line.split()
                    if len(elements) >= 1:
                        # The bridge name should be the first element after Bridge
                        br = elements[1]
                        break
        except Exception as e:
            print(f"Error in getting the bridge: {e}")

        # In order to get the ID of the switch, we will need to make
        # a dummy table entry with the MAC used for identification
        command = f"sudo ovs-ofctl -O OpenFlow13 add-flow {br} 'table=99, priority=0, mac, dl_src={self._mac}, actions=drop"

        try:
            # running the command for the dummy table
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to add flow: {str(e)}")

        # we will be utilizing the REST API to help retrieve the IDs
        # this REST API command used to retrieve list of switch ID's
        get_switches = f'http://{server_ADDR}:8080/stats/switches'
        # execute the REST command
        response_ = requests.get(get_switches)
        # all switch ID's should be here in this array
        switches = response_.json()

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

    # Part II.D: This method is used to retrieve the neighbors from BATMAN.
    def retrieve_client_neighbors(self):
        try:
            # executing the command to get the TQ from BATMAN
            output = subprocess.run(["sudo", "batctl", "o"],
                                    capture_output=True,
                                    text=True)

            # output to string
            text_output = output.stdout.strip()
            neigh_mac = []
            neigh_LQ = []

            # splits all lines into elements
            for line in text_output.split("\n"):
                # find the line with * which is the most optimal route that
                # the BATMAN routing algorithm has determined
                if line.lstrip().startswith("*"):
                    elements = line.split()

                    if len(elements) >= 5:
                        current_location = elements[1]
                        # this is for finding the next hop. Occasionally there
                        # is an odd bug where ( is counted as an element. This if
                        # is for this very specific case
                        if elements[3] == '(':
                            link_quality = elements[4].strip(")")
                            next_hop = elements[5]
                        # otherwise retrieve the MAC address of the next hop
                        else:
                            link_quality = elements[3].strip("()")
                            next_hop = elements[4]
                        if link_quality:
                            # if the next hop MAC is the same as the current, no need
                            # to put the next hop
                            if current_location == next_hop:
                                neigh_mac.append(current_location)
                            # else add the next hop
                            else:
                                neigh_mac.append([current_location, next_hop])

                            neigh_LQ.append(link_quality)

            return neigh_mac, neigh_LQ

        # Otherwise throw exception
        except Exception as e:
            print(f"Error trying to get BAT info: {e}")
            return None

    # Part II.C: This method is to create the neighbor tuple using the method
    # from part II.D.
    def return_device_neighbors(self):
        Mac, LQ = self.retrieve_client_neighbors()

        device_neighbors = {
            "nMAC": Mac,
            "LQ": LQ
        }

        return device_neighbors

    # Part II.B: Nier automata. This method is for updating our main data dictionary,
    # more specifically, the tuples.
    def make_device(self, subbed_neigh, subbed_xyz):
        # check if the neighbors were requested
        if subbed_neigh:
            # Update the neighbor tuple using this method
            device_neighbors = self.return_device_neighbors()
            self.device_info["Neighbor_Tuple"] = [True, device_neighbors]
        # else return false
        else:
            self.device_info["Neighbor_Tuple"] = [False]

        # check if the coordinates were requested
        if subbed_xyz:
            # create randomized value
            device_xyz = {
                "x": gen_random_number(0, 999),
                "y": gen_random_number(0, 999),
                "z": gen_random_number(0, 999)
            }
            self.device_info["XYZ_Tuple"] = [True, device_xyz]
        # else return false
        else:
            self.device_info["XYZ_Tuple"] = [False]

    # Part II.A: This method is used to communicate with the controller.
    def connection(self):
        first_connection = True
        while True:
            # create a socket object, this is for reconnection purposes
            # incase something goes wrong, we will try to reconnect to the controller
            client_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
            try:
                # attempt to connect
                client_socket.connect((self._ADDR, self._Port))
                while True:
                    # upon the first connection, the server will not
                    # send anything. We make sure to cycle through the first connection
                    if first_connection:
                        first_connection = False
                    else:
                        # checking the data we receive
                        data = client_socket.recv(1024)
                        if data:
                            conditions = json.loads(data.decode('utf-8'))
                            print(f"From server! {conditions}")

                            # conditions for the neighbors and drone coordinate
                            condition_neighbors = conditions[0]
                            condition_XYZ = conditions[1]

                            # make response dictionary for the controller
                            self.make_device(condition_neighbors, condition_XYZ)

                    # TODO: Optimize this to make it only send the TUPLES. The other datas should be static
                    # TODO: do not troll and try to actually do this
                    # Update, the original author trolled

                    # Send the data to the server
                    print(f"To server:\n{self.device_info}")
                    json_data = json.dumps(self.device_info)
                    client_socket.sendall(json_data.encode('utf-8'))

                    time.sleep(2)

            # Throw exception and close the current socket. Sleep for 5s then try again
            except sck.error:
                print(f"Error: {sck.error}")
                print(f"Retrying to connect to server: {self._ADDR}")
                client_socket.close()
                time.sleep(5)

# Main function that starts everything
if __name__ == "__main__":
    client = ClientHandler(server_ADDR, server_PORT)
    client.connection()
