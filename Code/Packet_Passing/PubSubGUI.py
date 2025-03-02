import copy

import customtkinter as ctk
import time
import socket as sck
import threading
import json
import subprocess

'''
Code sections are labeled in parts. Please start at 
Part I and then make your way to Part III.
'''

# This just gets the local IP for your server so you don't
# have to manually input it during test scenarios
def get_local_ip():
    try:
        s = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"Error: {e}")
        local_ip = "Unable to determine local IP"
    return local_ip

server_ADDR = "100.100.1.5"
nic_name = "wlp2s0"
server_PORT = 9559

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
theme_green = "#2ca373"

class DataTextScrollFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, title):
        super().__init__(master)
        self._local_data = []
        self._local_widgets = []
        self._local_length = 0
        self._title = title
        self.grid_columnconfigure(0, weight=1)

        self.title_display = ctk.CTkLabel(master=self,
                                          text=self._title,
                                          fg_color="cyan4",
                                          corner_radius=6)

        self.title_display.grid(column=0, padx=10, pady=(10, 0), sticky="we")

    def destroy_last_label(self):
        if len(self._local_widgets) > 0:
            self._local_widgets[-1].destroy()
            self._local_widgets.pop()

    def add_label(self, data):
        new_label = ctk.CTkLabel(master=self,
                                 text=f"{data}",
                                 fg_color="gray30",
                                 corner_radius=6)
        new_label.grid(column=0, padx=10, pady=(10, 0), sticky="we")
        self._local_widgets.append(new_label)

    def add_data(self, new_data):
        self._local_length = len(self._local_data)
        local_length = self._local_length
        new_data_length = len(new_data)

        # If local data is empty
        if not local_length:
            for i in new_data:
                new_label = ctk.CTkLabel(master=self,
                                         text=f"{i}",
                                         fg_color="gray30",
                                         corner_radius=6)
                new_label.grid(column=0, padx=10, pady=(10, 0), sticky="we")
                self._local_widgets.append(new_label)
        # If lengths of local data > new data
        elif local_length > new_data_length:
            change_length = local_length - new_data_length
            for _ in range(change_length):
                # Destroys last element
                self.destroy_last_label()
            self.update_data(new_data)
        # If lengths of local data < new data
        elif local_length < new_data_length:
            self.update_data(new_data[:local_length])
            remaining_data = new_data[local_length:]
            for data in remaining_data:
                self.add_label(data)
        # If lengths of local data == new data
        elif local_length == new_data_length:
            self.update_data(new_data)

        # Update local data
        self._local_data = list(new_data)

    def update_data(self, new_data):
        for index, btn in enumerate(self._local_widgets):
            btn.configure(text=f"{new_data[index]}")

    def clear_all_data(self):
        self._local_length = 0
        self._local_data = []

        if len(self._local_widgets) > 0:
            for btn in self._local_widgets:
                btn.destroy()
            self._local_widgets.clear()

# Part III: This is the data frame that is effected
# by the node switches (sub/unsub is here)
class DataFrame(ctk.CTkFrame):
    def __init__(self, master, client_dct):
        super().__init__(master)
        self._client_dct = client_dct
        self._saved_neighbor_text = {}
        self._saved_XYZ_text = {}
        self._current_device_info = {}
        self.subscribeNeighbor_pressed = False
        self.subscribeXYZ_pressed = False
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(2, weight=1)

        paddingX = 20
        paddingY = 20

        # This variable will be the width of all widgets in this frame
        column_width = 200

        # ---- These three widgets are identifications for what client we are using ----
        self.titleID = ctk.CTkLabel(master=self,
                                    text="ID: NONE",
                                    fg_color="gray30",
                                    width=column_width,
                                    corner_radius=6)

        self.titleMAC = ctk.CTkLabel(master=self,
                                     text="MAC: NONE",
                                     fg_color="gray30",
                                     width=column_width,
                                     corner_radius=6)

        self.titleIP = ctk.CTkLabel(master=self,
                                    text="IP: NONE",
                                    fg_color="gray30",
                                    width=column_width,
                                    corner_radius=6)

        self.titleID.grid(row=0, column=0,
                          padx=(paddingX, 5),
                          pady=paddingY,
                          sticky="we")

        self.titleMAC.grid(row=0, column=1,
                           padx=5,
                           pady=paddingY,
                           sticky="we")

        self.titleIP.grid(row=0, column=2,
                          padx=(5, paddingX),
                          pady=paddingY,
                          sticky="we")

        # ---- These three widgets are the subscribe, clear, and status widgets ----
        # for the neighbors
        self.subNeighbor_bt = ctk.CTkButton(master=self,
                                            text="Request Neighbors",
                                            fg_color="gray30",
                                            command=self.subscribeNeighbor_handler)

        self.clearNeighbor_bt = ctk.CTkButton(master=self,
                                              text="Clear Neighbors",
                                              command=self.clearNeighbor_handler)

        self.statusNeighbor_bt = ctk.CTkLabel(master=self,
                                              text="Unsubscribed",
                                              fg_color="firebrick1",
                                              corner_radius=6)

        self.subNeighbor_bt.grid(row=1, column=0,
                                 padx=(paddingX, 5),
                                 sticky="we")

        self.clearNeighbor_bt.grid(row=1, column=1,
                                   padx=5,
                                   sticky="we")

        self.statusNeighbor_bt.grid(row=1, column=2,
                                    padx=(5, paddingX),
                                    sticky="we")

        # ---- These are the text boxes for the data of XYZ ----
        self.text_neighbors_MAC = DataTextScrollFrame(self, "MAC")
        self.text_neighbors_MAC.grid(row=2, column=0, padx=(paddingX, 5), pady=paddingY, sticky="nsew")

        self.text_neighbors_IP = DataTextScrollFrame(self, "IP")
        self.text_neighbors_IP.grid(row=2, column=1, padx=5, pady=paddingY, sticky="nsew")

        self.text_neighbors_LQ = DataTextScrollFrame(self, "LQ")
        self.text_neighbors_LQ.grid(row=2, column=2, padx=(5, paddingX), pady=paddingY, sticky="nsew")

        # ---- These three widgets are the subscribe, clear, and status widgets ----
        # for the XYZ
        self.subXYZ_bt = ctk.CTkButton(master=self,
                                       text="Request XYZ",
                                       fg_color="gray30",
                                       command=self.subscribeXYZ_handler)

        self.clearXYZ_bt = ctk.CTkButton(master=self,
                                         text="Clear XYZ",
                                         command=self.clearXYZ_handler)

        self.statusXYZ_bt = ctk.CTkLabel(master=self,
                                         text="Unsubscribed",
                                         fg_color="firebrick1",
                                         corner_radius=6)

        self.clearXYZ_bt.grid(row=3, column=1,
                              padx=5,
                              sticky="we")

        self.subXYZ_bt.grid(row=3, column=0,
                            padx=(paddingX, 5),
                            sticky="we")

        self.statusXYZ_bt.grid(row=3, column=2,
                               padx=(5, paddingX),
                               sticky="we")

        # ---- These are the text boxes for the data of XYZ ----
        self.text_box_X = ctk.CTkFrame(master=self)
        self.text_box_Y = ctk.CTkFrame(master=self)
        self.text_box_Z = ctk.CTkFrame(master=self)

        self.text_box_X.grid(row=4, column=0,
                             padx=(paddingX, 5),
                             pady=paddingY,
                             sticky="we")

        self.text_box_Y.grid(row=4, column=1,
                             padx=5,
                             pady=paddingY,
                             sticky="we")

        self.text_box_Z.grid(row=4, column=2,
                             padx=(5, paddingX),
                             pady=paddingY,
                             sticky="we")

        # Dummy widget to control height
        xyz_height = 35
        self.text_label_X = ctk.CTkLabel(master=self.text_box_X,
                                         text="", height=xyz_height)
        self.text_label_X.pack(fill="both", expand=True)

        self.text_label_Y = ctk.CTkLabel(master=self.text_box_Y,
                                         text="", height=xyz_height)
        self.text_label_Y.pack(fill="both", expand=True)

        self.text_label_Z = ctk.CTkLabel(master=self.text_box_Z,
                                         text="", height=xyz_height)
        self.text_label_Z.pack(fill="both", expand=True)

    def print_client_dct(self):
        print("From data frame")
        for clientID, sub_dict_client in self._client_dct.items():
            print(f"{clientID}: {sub_dict_client}")

    def dropped_client_handler(self):
        self.subscribeNeighbor_pressed = False
        self.text_neighbors_MAC.clear_all_data()
        self.text_neighbors_IP.clear_all_data()
        self.text_neighbors_LQ.clear_all_data()

        self.subscribeXYZ_pressed = False
        self.text_label_X.configure(text="X:")
        self.text_label_Y.configure(text="Y:")
        self.text_label_Z.configure(text="Z:")

        self.titleID.configure(text="Disconnected")
        self.titleMAC.configure(text=f"MAC:")
        self.titleIP.configure(text=f"IP:")

        self.color_neighbors()
        self.color_XYZ()

    def update_client_ID(self, device_info,
                         client_dct,
                         first_click):

        self._current_device_info = device_info
        self._client_dct = client_dct
        client_id = self._current_device_info['ID']
        print(client_id)

        # This is the default states
        if first_click:
            self.subscribeNeighbor_pressed = False
            self.text_neighbors_MAC.clear_all_data()
            self.text_neighbors_IP.clear_all_data()
            self.text_neighbors_LQ.clear_all_data()

            self.subscribeXYZ_pressed = False
            self.text_label_X.configure(text="X:")
            self.text_label_Y.configure(text="Y:")
            self.text_label_Z.configure(text="Z:")

        else:
            Neighbor_state = self._current_device_info["Neighbor_Tuple"][0]
            XYZ_state = self._current_device_info["XYZ_Tuple"][0]

            if XYZ_state:
                self.subscribeXYZ_pressed = True
            else:
                self.subscribeXYZ_pressed = False

            if Neighbor_state:
                self.subscribeNeighbor_pressed = True
            else:
                self.subscribeNeighbor_pressed = False

            print(f"b4 clear: {self._saved_neighbor_text}")
            self.clearNeighbor_handler()

            print(f"after clear: {self._saved_neighbor_text}")
            self.display_neighbor(self._current_device_info["Neighbor_Tuple"],
                                  client_id)

            self.display_XYZ(self._current_device_info["XYZ_Tuple"],
                             client_id)

        self.titleID.configure(text=f"ID: {self._current_device_info['ID']}")
        self.titleMAC.configure(text=f"MAC: {self._current_device_info['MAC']}")
        self.titleIP.configure(text=f"IP: {self._current_device_info['IP']}")

        self.color_neighbors()
        self.color_XYZ()

    def subscribeNeighbor_handler(self):
        if len(self._current_device_info) > 0:
            device_ID = self._current_device_info["ID"]
            if not self.subscribeNeighbor_pressed:
                self.subscribeNeighbor_pressed = True
                self._client_dct[device_ID]["Neighbor_Tuple"][0] = True
            else:
                self.subscribeNeighbor_pressed = False
                self._client_dct[device_ID]["Neighbor_Tuple"] = [False]

            self.color_neighbors()

    def color_neighbors(self):
        if self.subscribeNeighbor_pressed:
            self.subNeighbor_bt.configure(fg_color=theme_green)
            self.statusNeighbor_bt.configure(text="Subscribed",
                                             fg_color=theme_green)
        else:
            self.subNeighbor_bt.configure(fg_color="firebrick1")
            self.statusNeighbor_bt.configure(text="Unsubscribed",
                                             fg_color="firebrick1")

    def add_neighbor_data(self, mac, ip, lq):
        self.text_neighbors_MAC.add_data(mac)
        self.text_neighbors_IP.add_data(ip)
        self.text_neighbors_LQ.add_data(lq)

    def clearNeighbor_handler(self):
        self.text_neighbors_MAC.clear_all_data()
        self.text_neighbors_IP.clear_all_data()
        self.text_neighbors_LQ.clear_all_data()

    def display_neighbor(self, data_from_main, client_id):
        if data_from_main:
            status = data_from_main[0]
            data_length = len(data_from_main)
            print(f"from client {client_id}")
            # For the rare scenario where the client has no neighbors
            if status and (data_length == 1):
                print("true condition no neighbors")
                self.clearNeighbor_handler()
            # For new subscribe entries
            elif status and (data_length > 1):
                print("true condition")
                neighMAC = data_from_main[1]["nMAC"]
                neighIP = data_from_main[1]["nIP"]
                neighLQ = data_from_main[1]["LQ"]
                # If the temporary data empty, add to it
                if client_id not in self._saved_neighbor_text:
                    print("empty save neighbors add")
                    self._saved_neighbor_text[client_id] = {
                        "nMAC": list(neighMAC),
                        "nIP": list(neighIP),
                        "LQ": list(neighLQ)
                    }
                    self.add_neighbor_data(list(neighMAC),
                                           list(neighIP),
                                           list(neighLQ))
                # If there already is data in the temp variable,
                # go to check what needs to be replaced
                else:
                    print("non empty neighbor list")
                    '''
                    tempIP = self._saved_neighbor_text[client_id]["nIP"]

                    # Check if we need to replace
                    if neighIP == tempIP:
                        print("identical IPs, changing LQ")
                        # If the list of IPs are identical, only update LQ
                        self._saved_neighbor_text[client_id]["LQ"] = list(neighLQ)
                        self.text_neighbors_LQ.update_data(list(neighLQ))
                    # If they are not equal, replace every element
                    else:
                    '''
                    print("non identical IP, change everything")
                    self._saved_neighbor_text[client_id] = {
                        "nMAC": list(neighMAC),
                        "nIP": list(neighIP),
                        "LQ": list(neighLQ)
                    }
                    print(f"b4 add: {self._saved_neighbor_text[client_id]}")
                    self.add_neighbor_data(list(neighMAC),
                                           list(neighIP),
                                           list(neighLQ))
                    print(f"after add: {self._saved_neighbor_text[client_id]}")
            elif not status:
                print("false handler")
                if ((len(self._saved_neighbor_text) > 0) and
                        (client_id in self._saved_neighbor_text)):
                    nMAC = self._saved_neighbor_text[client_id]["nMAC"]
                    nIP = self._saved_neighbor_text[client_id]["nIP"]
                    nLQ = self._saved_neighbor_text[client_id]["LQ"]

                    print("save state")
                    print(f"{nMAC}, {nIP}, {nLQ}")
                    self.add_neighbor_data(list(nMAC), list(nIP), list(nLQ))
                else:
                    print("emptiness")
                    self.clearNeighbor_handler()


    def subscribeXYZ_handler(self):
        if len(self._current_device_info) > 0:
            device_ID = self._current_device_info["ID"]
            if not self.subscribeXYZ_pressed:
                self.subscribeXYZ_pressed = True
                self._client_dct[device_ID]["XYZ_Tuple"][0] = True
            else:
                self.subscribeXYZ_pressed = False
                self._client_dct[device_ID]["XYZ_Tuple"] = [False]

            self.color_XYZ()

    def color_XYZ(self):
        if self.subscribeXYZ_pressed:
            self.subXYZ_bt.configure(fg_color=theme_green)
            self.statusXYZ_bt.configure(text="Subscribed",
                                        fg_color=theme_green)
        else:
            self.subXYZ_bt.configure(fg_color="firebrick1")
            self.statusXYZ_bt.configure(text="Unsubscribed",
                                        fg_color="firebrick1")

    # This method handles the printing of data on the screen
    def display_XYZ(self, data_from_main, client_id):
        if data_from_main:
            status = data_from_main[0]
            has_data = len(data_from_main)

            if status and (has_data > 1):
                new_X = data_from_main[1]['x']
                new_Y = data_from_main[1]['y']
                new_Z = data_from_main[1]['z']
                self._saved_XYZ_text[client_id] = {
                    "x": new_X,
                    "y": new_Y,
                    "z": new_Z
                }
                self.text_label_X.configure(
                    text=f"X: {new_X}"
                )
                self.text_label_Y.configure(
                    text=f"Y: {new_Y}"
                )
                self.text_label_Z.configure(
                    text=f"Z: {new_Z}"
                )
            elif not status:
                if ((len(self._saved_XYZ_text) > 0) and
                        (client_id in self._saved_XYZ_text)):
                    self.text_label_X.configure(
                        text=f"X: {self._saved_XYZ_text[client_id]['x']}"
                    )
                    self.text_label_Y.configure(
                        text=f"Y: {self._saved_XYZ_text[client_id]['y']}"
                    )
                    self.text_label_Z.configure(
                        text=f"Z: {self._saved_XYZ_text[client_id]['z']}"
                    )
                else:
                    self.text_label_X.configure(
                        text=f"X:"
                    )
                    self.text_label_Y.configure(
                        text=f"Y:"
                    )
                    self.text_label_Z.configure(
                        text=f"Z:"
                    )

    def clearXYZ_handler(self):
        self.text_label_X.configure(text=f"")
        self.text_label_Y.configure(text=f"")
        self.text_label_Z.configure(text=f"")

# Part II: This is the frame class of the switches / nodes themselves
# The left section with the green buttons
class SwitchFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, data_frame, client_dct):
        super().__init__(master)
        self._current_client = {}
        self._current_ID = 0
        self._client_dct = client_dct
        self._data_frame = data_frame
        self._first_click_tracker = []
        self._client_btn = {}
        self.grid_columnconfigure(0, weight=1)
        self.title = ctk.CTkButton(master=self, text="B.A.T.M.A.N Switches", fg_color="gray30", corner_radius=6)
        self.title.grid(column=0, padx=10, pady=(10, 0), sticky="ew")

    def return_current_ID(self):
        return self._current_ID

    def set_current_client(self, client_id):
        # device_info packet from client code
        self._current_ID = client_id
        self._current_client = self._client_dct[self._current_ID]

        f_clk = True
        obj_ind = 0

        for index, i in enumerate(self._first_click_tracker):
            if i[0] == client_id:
                f_clk = i[1]
                obj_ind = index

        if f_clk:
            self._first_click_tracker[obj_ind][1] = False

        self._data_frame.update_client_ID(self._current_client,
                                          self._client_dct,
                                          f_clk)

    # This method adds newly arrived clients and creates a button
    # It uses dictionaries to quickly search for the ID
    def add_client_button(self, c_list):
        client_information = copy.copy(c_list)
        clientID = client_information["ID"]

        if clientID not in self._client_dct:
            btn = ctk.CTkButton(master=self,
                                text=f"{clientID}",
                                corner_radius=6)
            btn.grid(column=0, padx=10, pady=(10, 0), sticky="ew")

            '''
            This is an anonymous function
            lambda argument: expression
            Anon functions are nameless functions that are basically one lined functions 
            that spits out a result once activated
            '''
            btn.configure(command=lambda x=clientID: self.set_current_client(x))

            '''
            ATTENTION: This is how the dictionary is made 
            dict{"ID from the switch": "btn": the buttons, "data": data from switch}
            client_dct[ID]["data"][your choice] 
            '''
            self._client_btn[clientID] = {"btn": btn}
            self._client_dct[clientID] = {"ID": client_information["ID"],
                                          "MAC": client_information["MAC"],
                                          "IP": client_information["IP"],
                                          "Neighbor_Tuple": client_information["Neighbor_Tuple"],
                                          "XYZ_Tuple": client_information["XYZ_Tuple"]}
            self._first_click_tracker.append([clientID, True])

    # This method deletes client button and clears it from the dictionary
    def del_client_button(self, client_information):
        self._current_ID = 0
        clientID = client_information["ID"]

        if clientID in self._client_btn:
            if self._client_btn[clientID]["btn"]:
                self._client_btn[clientID]["btn"].destroy()

                del self._client_btn[clientID]["btn"]

# Part I: This is the main class that handles all the incoming clients. Each client is treated as a thread
class PubSubGUI(ctk.CTk):
    def __init__(self, addr, port):
        super().__init__()
        self._ADDR = addr
        self._Port = port

        self.title("Publish Subscribe WMN GUI")
        self.geometry("1000x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._client_dct = {}
        self._client_MAC_IP = {self.retrieve_client_MAC(): server_ADDR}
        self._client_updated = {}

        # object for part III
        self.data_frame = DataFrame(self, self._client_dct)
        self.data_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # object for part II
        self.switch_frame = SwitchFrame(self, self.data_frame, self._client_dct)
        self.switch_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        time.sleep(0.01)
        BAT_server = threading.Thread(target=self.BATMAN_server_handler, args=())
        BAT_server.start()

        time.sleep(0.01)
        self.client_frames_handler()

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

    def update_client_dct(self, client_information):
        clientID = client_information["ID"]

        if clientID in self._client_dct:
            server_neighbor_tuple = self._client_dct[clientID]["Neighbor_Tuple"][0]
            client_neighbor_tuple = client_information["Neighbor_Tuple"][0]
            server_XYZ_tuple = self._client_dct[clientID]["XYZ_Tuple"][0]
            client_XYZ_tuple = client_information["XYZ_Tuple"][0]

            if server_neighbor_tuple and client_neighbor_tuple:
                self._client_dct[clientID]["Neighbor_Tuple"] = copy.copy(client_information["Neighbor_Tuple"])
                for index, existing_mac in enumerate(
                        self._client_dct[clientID]["Neighbor_Tuple"][1]["nMAC"]
                ):
                    if existing_mac in self._client_MAC_IP:
                        self._client_dct[clientID]["Neighbor_Tuple"][1]["nIP"][index] = (
                            self._client_MAC_IP)[existing_mac]
            elif not server_neighbor_tuple:
                self._client_dct[clientID]["Neighbor_Tuple"] = [False]
            if server_XYZ_tuple and client_XYZ_tuple:
                self._client_dct[clientID]["XYZ_Tuple"] = client_information["XYZ_Tuple"]
            elif not server_XYZ_tuple:
                self._client_dct[clientID]["XYZ_Tuple"] = [False]

    def client_frames_handler(self):
        current_client_ID = self.switch_frame.return_current_ID()
        # If we have a current client, update the clients
        if current_client_ID and (current_client_ID in self._client_updated):
            if self._client_updated[current_client_ID]["updated"]:
                self.data_frame.display_neighbor(self._client_dct[current_client_ID]["Neighbor_Tuple"],
                                                 current_client_ID)
                self.data_frame.display_XYZ(self._client_dct[current_client_ID]["XYZ_Tuple"],
                                            current_client_ID)
                self._client_updated[current_client_ID]["updated"] = False

        self.after(500, self.client_frames_handler)

    # Simple print function
    def print_client_dct(self, client_id):
        print(f"From main - {client_id}")
        for clientID, sub_dict_client in self._client_dct.items():
            print(f"{clientID}: {sub_dict_client['Neighbor_Tuple']}")

    # Part I.B: This is where each thread goes to be processed
    def BATMAN_Client_Handler_Thread(self, client_obj, addr):
        # This dictionary is for request handling
        data_req = {
            "Req_Neigh": False,
            "Req_XYZ": False
        }

        first_connection = True
        bat_pack = {}
        currentID = 0

        try:
            while True:
                # Checking for neighbors or XYZ conditions
                data = client_obj.recv(1024)

                bat_pack = json.loads(data.decode('utf-8'))
                currentID = bat_pack["ID"]

                if first_connection:
                    # If it's the first connection, we add the client as a button
                    self.switch_frame.add_client_button(bat_pack)
                    self._client_MAC_IP[bat_pack["MAC"]] = bat_pack["IP"]
                    first_connection = False
                else:
                    # If it isn't, client dictionary is updated
                    self.update_client_dct(copy.copy(bat_pack))
                    time.sleep(0.001)
                    self._client_updated[currentID] = {
                        "updated": True
                    }

                #self.print_client_dct(bat_pack["ID"])

                # Request handling, checking our current dictionary if we need to ask
                # the client to send neighbor or XYZ data
                if self._client_dct[currentID]["Neighbor_Tuple"][0]:
                    data_req["Req_Neigh"] = True
                else:
                    data_req["Req_Neigh"] = False

                if self._client_dct[currentID]["XYZ_Tuple"][0]:
                    data_req["Req_XYZ"] = True
                else:
                    data_req["Req_XYZ"] = False

                # Sends dictionary request handler
                json_data = json.dumps(data_req)
                client_obj.sendall(json_data.encode('utf-8'))

                time.sleep(3)
        except Exception as e:
            print(f"Lost connection at {addr}: {e}")

        try:
            self.switch_frame.del_client_button(bat_pack)
        except Exception as e:
            print(f"Error deleting btn, client [{addr}]")

        if currentID in self._client_dct:
            del self._client_dct[currentID]

        client_obj.close()

    # Part I.A: This is the main server socket that will create threads for each client connected
    def BATMAN_server_handler(self):
        server_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        server_socket.bind((self._ADDR, self._Port))
        server_socket.listen()

        # Handler for the connected client objects
        while True:
            client_obj, address = server_socket.accept()
            sub_thread = threading.Thread(target=self.BATMAN_Client_Handler_Thread,
                                          args=(client_obj, address))
            sub_thread.start()

if __name__ == "__main__":
    gui = PubSubGUI(server_ADDR, server_PORT)
    gui.mainloop()