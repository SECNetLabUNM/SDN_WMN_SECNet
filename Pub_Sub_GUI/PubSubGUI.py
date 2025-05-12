import copy
import customtkinter as ctk
import time
import socket as sck
import threading
import json
import random
import subprocess

'''
Code sections are labeled in parts. Please start at 
Part I and then make your way to Part III.
'''

def retrieve_client_MAC():
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

def gen_random_number(flr, ceil):
    return random.randint(flr, ceil)


server_ADDR = "100.100.1.5"
nic_name = "wlp2s0"
server_PORT = 9559
server_MAC = retrieve_client_MAC()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
theme_green = "#2ca373"

MAC_2_IP_ID_CLR = {}
# Types: 0 = RYU ID, 1 = MAC, 2 = IP
# Boolean for if updated
Type_Change = [1, False]

# 20 total different colors. Please add more if you need more variation.
# CHECK HERE FOR SPELLING ERRORS
color_list = [
    "midnight blue", "cornflower blue", "dodger blue", "dark green", "dark olive green",
    "forest green", "olive drab", "indian red", "saddle brown", "orange red",
    "hot pink", "pale violet red", "hot pink", "dark orchid", "medium purple",
    "AntiqueWhite4", "NavajoWhite4", "LightGoldenrod4", "burlywood4", "brown4",
    "maroon4", "plum4", "gray1", "gray15", "gray60"
]
# Part V: this class is the neighbor frame that hosts all the widgets that
# can be added or subtracted
class NeighborTextScrollFrame(ctk.CTkScrollableFrame):
    # Part V.A: default constructor
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

    # Part V.B.a: used as a "pop" to erase a widget
    def destroy_last_label(self):
        if len(self._local_widgets) > 0:
            self._local_widgets[-1].destroy()
            self._local_widgets.pop()

    # Part V.B.b: used as a "append" to add more widgets
    def add_label(self, data):
        new_label = ctk.CTkLabel(master=self,
                                 text=f"{data}",
                                 fg_color="gray30",
                                 corner_radius=6)
        new_label.grid(column=0, padx=10, pady=(10, 0), sticky="we")
        self._local_widgets.append(new_label)

    # Part V.B.c: used for overwriting existing widgets
    def update_data(self, new_data):
        for index, btn in enumerate(self._local_widgets):
            btn.configure(text=f"{new_data[index]}")

    # Part V.B: this method is sued to determine if we need to add more
    # widgets or delete them
    def add_data(self, new_data):
        self._local_length = len(self._local_data)
        local_length = self._local_length
        new_data_length = len(new_data)

        # If local data is empty
        if not local_length:
            for i in new_data:
                self.add_label(i)

        # If lengths of local data > new data, add more widgets
        elif local_length > new_data_length:
            change_length = local_length - new_data_length
            for _ in range(change_length):
                # Destroys last element
                self.destroy_last_label()
            self.update_data(new_data)
        # If lengths of local data < new data, delete widgets
        elif local_length < new_data_length:
            self.update_data(new_data[:local_length])
            remaining_data = new_data[local_length:]
            for data in remaining_data:
                self.add_label(data)
        # If lengths of local data == new data, overwrite existing widgets
        elif local_length == new_data_length:
            self.update_data(new_data)

        # Update local data
        self._local_data = list(new_data)

    # Part V.C: this method is used for clearing ALL widgets
    def clear_all_data(self):
        self._local_length = 0
        self._local_data = []

        if len(self._local_widgets) > 0:
            for btn in self._local_widgets:
                btn.destroy()
            self._local_widgets.clear()

    # Part V.D: this method is used to update the widget color of the neighbors
    def update_color(self, new_color):
        for i, btn in enumerate(self._local_widgets):
            btn.configure(fg_color=new_color[i])

# Part VI: this class handles the drone coordinate data
class XYZTextFrame(ctk.CTkFrame):
    # Part VI.A: default constructor
    def __init__(self, master, title):
        super().__init__(master, height=45)
        self._title = title
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.title_display = ctk.CTkLabel(master=self,
                                          text=self._title,
                                          fg_color="cyan4",
                                          corner_radius=6,
                                          width=35)

        self.title_display.grid(column=0,
                                row=0,
                                padx=(10, 0),
                                pady=10)

        self.text_label = ctk.CTkLabel(master=self,
                                       text="",
                                       fg_color="gray30",
                                       corner_radius=6)

        self.text_label.grid(column=1,
                             row=0,
                             padx=10,
                             pady=10,
                             sticky="we")

    # Part VI.B: this method used to update the text widget
    def update_text(self, text):
        self.text_label.configure(text=text)

    # Part VI.C: this method is used for clearing the text
    def clear_text(self):
        self.text_label.configure(text="")

# Part IV: this frame is the three buttons you see on top as ID, MAC, IP
class TitleTextFrame(ctk.CTkFrame):
    # Part IV.A: default constructor
    def __init__(self, master, title):
        super().__init__(master, height=45)
        self._title = title
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.title_display = ctk.CTkButton(master=self,
                                           text=self._title,
                                           corner_radius=6,
                                           command=lambda: self.change_display_type(),
                                           width=35)

        self.title_display.grid(column=0,
                                row=0,
                                padx=(10, 0),
                                pady=10)

        self.text_label = ctk.CTkLabel(master=self,
                                       text="",
                                       fg_color="gray30",
                                       corner_radius=6)

        self.text_label.grid(column=1,
                             row=0,
                             padx=10,
                             pady=10,
                             sticky="we")

    # Part IV.B: this method is used for changing the text
    def update_text(self, text):
        self.text_label.configure(text=text)

    # Part IV.C: this method is used for changing the types
    def change_display_type(self):
        global Type_Change
        if self._title == "ID":
            Type_Change[0] = 0
        elif self._title == "MAC":
            Type_Change[0] = 1
        elif self._title == "IP":
            Type_Change[0] = 2

        Type_Change[1] = True

    # Part IV.D: this method is used for changing the color
    def change_color(self, clr):
        self.title_display.configure(fg_color=clr)

# Part III: This is the data frame that is effected
# by the node switches (sub/unsub is here)
class DataFrame(ctk.CTkFrame):
    # Part III.A: default constructor to create the frame
    def __init__(self, master, client_dct):
        super().__init__(master)
        # Variables that will be crucial for later
        self._client_dct = client_dct
        self._current_ID = 0
        self._current_MAC = ""
        self._saved_neighbor_text = {}
        self._saved_XYZ_text = {}
        self._current_device_info = {}
        self.subscribeNeighbor_pressed = False
        self.subscribeXYZ_pressed = False
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(2, weight=1)

        paddingX = 20
        paddingY = 20

        # These three widgets are identifications for what client we are using
        # This class is part IV
        self.titleID = TitleTextFrame(self, "ID")
        self.titleMAC = TitleTextFrame(self, "MAC")
        self.titleIP = TitleTextFrame(self, "IP")

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

        # These three widgets are the subscribe, clear, and status widgets
        # for the neighbors
        self.subNeighbor_bt = ctk.CTkButton(master=self,
                                            text="Request Neighbors",
                                            fg_color="gray30",
                                            command=self.subscribe_neighbor_handler)

        self.clearNeighbor_bt = ctk.CTkButton(master=self,
                                              text="Clear Neighbors",
                                              command=self.clear_all_neighbor_data)

        self.statusNeighbor_bt = ctk.CTkLabel(master=self,
                                              text="Not Requesting",
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

        # These are the text boxes for the data for the neighbors. This is
        # a CTkinter class created in part V
        self.text_neighbors_Origin = NeighborTextScrollFrame(self, "Originator")
        self.text_neighbors_Origin.grid(row=2,
                                        column=0,
                                        padx=(paddingX, 5),
                                        pady=paddingY,
                                        sticky="nsew")

        self.text_neighbors_Next_Hop = NeighborTextScrollFrame(self, "Next Hop")
        self.text_neighbors_Next_Hop.grid(row=2,
                                          column=1,
                                          padx=5,
                                          pady=paddingY,
                                          sticky="nsew")

        self.text_neighbors_LQ = NeighborTextScrollFrame(self, "Link Quality")
        self.text_neighbors_LQ.grid(row=2,
                                    column=2,
                                    padx=(5, paddingX),
                                    pady=paddingY,
                                    sticky="nsew")

        # These three widgets are the subscribe, clear, and status widgets
        # for the XYZ
        self.subXYZ_bt = ctk.CTkButton(master=self,
                                       text="Request XYZ",
                                       fg_color="gray30",
                                       command=self.subscribe_XYZ_handler)

        self.clearXYZ_bt = ctk.CTkButton(master=self,
                                         text="Clear XYZ",
                                         command=self.clear_all_XYZ_data)

        self.statusXYZ_bt = ctk.CTkLabel(master=self,
                                         text="Not Requesting",
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

        # These are the text boxes for the data of XYZ. This is a CTKinter
        # class created in part VI
        self.text_label_X = XYZTextFrame(self, "X")
        self.text_label_Y = XYZTextFrame(self, "Y")
        self.text_label_Z = XYZTextFrame(self, "Z")

        self.text_label_X.grid(row=4, column=0,
                               padx=(paddingX, 5),
                               pady=paddingY,
                               sticky="we")

        self.text_label_Y.grid(row=4, column=1,
                               padx=5,
                               pady=paddingY,
                               sticky="we")

        self.text_label_Z.grid(row=4, column=2,
                               padx=(5, paddingX),
                               pady=paddingY,
                               sticky="we")

    # print method for debugging
    def print_client_dct(self):
        print("From data frame")
        for clientID, sub_dict_client in self._client_dct.items():
            print(f"{clientID}: {sub_dict_client}")

    # Part III.B: this method is for updating the current client.
    # it is used as a bridge for part II where the buttons used in part II uses
    # this method to change the current client to handle
    def update_client_ID(self,
                         device_info,
                         client_dct,
                         first_click):

        self._current_device_info = device_info
        self._client_dct = client_dct
        self._current_ID = self._current_device_info['ID']
        self._current_MAC = self._current_device_info['MAC']

        # "first click" state, set the subscribe states to false and clears
        # all widgets
        if first_click:
            self.subscribeNeighbor_pressed = False
            self.subscribeXYZ_pressed = False

            self.clear_neighbor_handler()
            self.clear_XYZ_handler()

        # Otherwise update this frame with the latest data.
        # This scenario is when we switch between hosts from part II and is primarily
        # used by part II only
        else:
            # take the current data from the tuples
            Neighbor_state = self._current_device_info["Neighbor_Tuple"][0]
            XYZ_state = self._current_device_info["XYZ_Tuple"][0]

            # check the states
            if XYZ_state:
                self.subscribeXYZ_pressed = True
            else:
                self.subscribeXYZ_pressed = False

            if Neighbor_state:
                self.subscribeNeighbor_pressed = True
            else:
                self.subscribeNeighbor_pressed = False

            # b/c this method is usually called when a new host is selected from
            # part II, we must clear all widgets and start the display process
            # again
            self.clear_neighbor_handler()
            self.clear_XYZ_handler()

            # Method used for adding/updating the neighbor data
            self.display_neighbor(self._current_device_info["Neighbor_Tuple"],
                                  self._current_ID)

            # Method used for adding/updating the XYZ data
            self.display_XYZ(self._current_device_info["XYZ_Tuple"],
                             self._current_ID)

        # Update the title frame classes for when we switch
        self.titleID.update_text(self._current_device_info['ID'])
        self.titleMAC.update_text(self._current_device_info['MAC'])
        self.titleIP.update_text(self._current_device_info['IP'])

        # Find the color for the device
        current_color = MAC_2_IP_ID_CLR[self._current_MAC]["Color"]

        # Update the color of the widgets
        self.titleID.change_color(current_color)
        self.titleMAC.change_color(current_color)
        self.titleIP.change_color(current_color)

        # Update the color of the sub buttons based on the subscribe state
        self.color_neighbors()
        self.color_XYZ()

    # Part III.C: this method is to handle subscriptions for the subscribe button
    # of the neighbor portion
    def subscribe_neighbor_handler(self):
        if len(self._current_device_info) > 0:
            device_ID = self._current_device_info["ID"]
            if not self.subscribeNeighbor_pressed:
                self.subscribeNeighbor_pressed = True
                self._client_dct[device_ID]["Neighbor_Tuple"][0] = True
            else:
                self.subscribeNeighbor_pressed = False
                self._client_dct[device_ID]["Neighbor_Tuple"] = [False]

            # Update widget color
            self.color_neighbors()

    # Part III.D: this method is used to update the color of the subscribe and
    # status widgets of the neighbors
    def color_neighbors(self):
        if self.subscribeNeighbor_pressed:
            self.subNeighbor_bt.configure(fg_color=theme_green)
            self.statusNeighbor_bt.configure(text="Requesting Neighbors",
                                             fg_color=theme_green)
        else:
            self.subNeighbor_bt.configure(fg_color="firebrick1")
            self.statusNeighbor_bt.configure(text="Paused Neighbors",
                                             fg_color="firebrick1")

    # Part III.E: this method is the primary
    def display_neighbor(self, data_from_main, client_id):
        if data_from_main:
            status = data_from_main[0]
            data_length = len(data_from_main)
            # For the rare scenario where the client has no neighbors
            if status and (data_length == 1):
                self.clear_neighbor_handler()
            # For new subscribe entries
            elif status and (data_length > 1):
                neighMAC = data_from_main[1]["nMAC"]
                neighLQ = data_from_main[1]["LQ"]
                # If there is a new ID/host, add to the saved data dict
                if client_id not in self._saved_neighbor_text:
                    # This dict is used to save the current data with respects
                    # to the client id
                    self._saved_neighbor_text[client_id] = {
                        "nMAC": list(neighMAC),
                        "LQ": list(neighLQ)
                    }
                    self.add_neighbor_data(list(neighMAC),
                                           list(neighLQ))
                # If the ID/host is already in the saved dict,
                # we just need to update its current data
                else:
                    self._saved_neighbor_text[client_id] = {
                        "nMAC": list(neighMAC),
                        "LQ": list(neighLQ)
                    }
                    self.add_neighbor_data(list(neighMAC),
                                           list(neighLQ))
            # Unsubscribe state. We need to save the existing data
            # that is already on the screen rather than wiping it.
            # Note, this saved data will also be from host to host
            # so if you switch between each host, their saved data will
            # be displayed
            elif not status:
                if ((len(self._saved_neighbor_text) > 0) and
                        (client_id in self._saved_neighbor_text)):
                    nMAC = self._saved_neighbor_text[client_id]["nMAC"]
                    nLQ = self._saved_neighbor_text[client_id]["LQ"]

                    self.add_neighbor_data(list(nMAC),
                                           list(nLQ))

                else:
                    self.clear_neighbor_handler()

    # Part F.a: this method is adjusting the selected types
    def append_on_type(self, type_cond, mac_addr):
        global MAC_2_IP_ID_CLR
        return_value = ""

        if type_cond == 0:
            return_value = MAC_2_IP_ID_CLR[mac_addr]["ID"]
        elif type_cond == 1:
            return_value = mac_addr
        elif type_cond == 2:
            return_value = MAC_2_IP_ID_CLR[mac_addr]["IP"]

        return return_value

    # Part III.F: this method is used for adding/updating the data widgets
    # seen in part V
    def add_neighbor_data(self, mac, lq):
        global Type_Change
        global MAC_2_IP_ID_CLR

        temp_lq = list(lq)

        origin_list = []
        color_list_or = []

        next_hop_list = []
        color_list_nh = []

        link_quality_list = []

        # Going through the MAC list
        for index, m in enumerate(mac):
            # If the MAC list has two separate MACs or is basically a list
            # we know that it requires multi-hop to reach the current host
            if isinstance(m, list):
                if m[0] in MAC_2_IP_ID_CLR and m[1] in MAC_2_IP_ID_CLR:
                    # Origin list handling
                    origin_list.append(
                        self.append_on_type(Type_Change[0], m[0])
                    )

                    # Color list handling
                    color_list_or.append(
                        MAC_2_IP_ID_CLR[m[0]]["Color"]
                    )

                    # Next hop list handling
                    next_hop_list.append(
                        self.append_on_type(Type_Change[0], m[1])
                    )
                    color_list_nh.append(
                        MAC_2_IP_ID_CLR[m[1]]["Color"]
                    )

                    # Link quality list handling
                    link_quality_list.append(temp_lq[index])
            else:
                # This is for one hop condition handling. We know that
                # if only 1 MAC address, Batman IV has determined that
                # one hop is ideal
                if m in MAC_2_IP_ID_CLR:
                    # Origin list handling
                    origin_list.append(
                        self.append_on_type(Type_Change[0], m)
                    )
                    # Color list handling
                    color_list_or.append(MAC_2_IP_ID_CLR[m]["Color"])

                    # Next hop list handling
                    next_hop_list.append(
                        self.append_on_type(Type_Change[0], self._current_MAC)
                    )

                    color_list_nh.append(
                        MAC_2_IP_ID_CLR[self._current_MAC]["Color"]
                    )

                    # Link quality list handling
                    link_quality_list.append(temp_lq[index])

        # Change the frame class based on the new lists
        self.text_neighbors_Origin.add_data(origin_list)
        self.text_neighbors_Origin.update_color(color_list_or)
        self.text_neighbors_Next_Hop.add_data(next_hop_list)
        self.text_neighbors_Next_Hop.update_color(color_list_nh)
        self.text_neighbors_LQ.add_data(link_quality_list)
        self.text_neighbors_LQ.update_color(color_list_or)

    # Part III.G: this method is used for clearing data
    def clear_neighbor_handler(self):
        self.text_neighbors_Origin.clear_all_data()
        self.text_neighbors_Next_Hop.clear_all_data()
        self.text_neighbors_LQ.clear_all_data()

    # Part III.H: this method is used for clearing data but it's for the button
    def clear_all_neighbor_data(self):
        self.text_neighbors_Origin.clear_all_data()
        self.text_neighbors_Next_Hop.clear_all_data()
        self.text_neighbors_LQ.clear_all_data()
        if self._current_ID in self._saved_neighbor_text:
            self._saved_neighbor_text[self._current_ID] = {
                "nMAC": [],
                "LQ": []
            }

    # Part III.I: this method is used for handling the subscriptions for the
    # subscribe button of the XYZ portion
    def subscribe_XYZ_handler(self):
        if len(self._current_device_info) > 0:
            device_ID = self._current_device_info["ID"]
            if not self.subscribeXYZ_pressed:
                self.subscribeXYZ_pressed = True
                self._client_dct[device_ID]["XYZ_Tuple"][0] = True
            else:
                self.subscribeXYZ_pressed = False
                self._client_dct[device_ID]["XYZ_Tuple"] = [False]

            self.color_XYZ()

    # Part III.J: this method is used to update the color of the subscribe and
    # status widgets of the XYZ portion
    def color_XYZ(self):
        if self.subscribeXYZ_pressed:
            self.subXYZ_bt.configure(fg_color=theme_green)
            self.statusXYZ_bt.configure(text="Requesting XYZ",
                                        fg_color=theme_green)
        else:
            self.subXYZ_bt.configure(fg_color="firebrick1")
            self.statusXYZ_bt.configure(text="Paused XYZ",
                                        fg_color="firebrick1")

    # Part III.K: this method handles the printing of the XYZ data on the screen
    def display_XYZ(self, data_from_main, client_id):
        if data_from_main:
            status = data_from_main[0]
            has_data = len(data_from_main)

            # Subscribed state. Same idea as the neighbors
            if status and (has_data > 1):
                new_X = data_from_main[1]['x']
                new_Y = data_from_main[1]['y']
                new_Z = data_from_main[1]['z']

                # Update saves with new coordinate data
                self._saved_XYZ_text[client_id] = {
                    "x": new_X,
                    "y": new_Y,
                    "z": new_Z
                }
                # Add to the frame
                self.add_XYZ_data(new_X, new_Y, new_Z)

            # Unsubscribe state
            elif not status:
                # If there is actually data in the save state, update
                if ((len(self._saved_XYZ_text) > 0) and
                        (client_id in self._saved_XYZ_text)):
                    saved_X = self._saved_XYZ_text[client_id]['x']
                    saved_Y = self._saved_XYZ_text[client_id]['y']
                    saved_Z = self._saved_XYZ_text[client_id]['z']

                    self.add_XYZ_data(saved_X, saved_Y, saved_Z)
                # If there is none, just clear the XYZ portion
                else:
                    self.clear_XYZ_handler()

    # Part III.L: this method is used to send the new XYZ data into the
    # class frame in part VI
    def add_XYZ_data(self, x, y, z):
        self.text_label_X.update_text(x)
        self.text_label_Y.update_text(y)
        self.text_label_Z.update_text(z)

    # Part III.M: method used for deleting clearing the XYZ frame
    def clear_XYZ_handler(self):
        self.text_label_X.clear_text()
        self.text_label_Y.clear_text()
        self.text_label_Z.clear_text()

    # Part III.N: method used for deleting clearing the XYZ frame used by the
    # clear button
    def clear_all_XYZ_data(self):
        self.text_label_X.clear_text()
        self.text_label_Y.clear_text()
        self.text_label_Z.clear_text()

        if self._current_ID in self._saved_XYZ_text:
            self._saved_XYZ_text[self._current_ID] = {
                "x": [],
                "y": [],
                "z": []
            }

# Part II: This is the frame class of the switches / nodes themselves
# The left section with the green buttons
class SwitchFrame(ctk.CTkScrollableFrame):
    # Part II.A: this is the default constructor that sets up
    # the frame and its size
    def __init__(self, master, data_frame, client_dct):
        super().__init__(master)
        self._current_client = {}
        self._current_ID = 0
        self._client_dct = client_dct
        self._data_frame = data_frame
        self._first_click_tracker = []
        self._client_btn = {}
        self.grid_columnconfigure(0, weight=1)
        self.title = ctk.CTkLabel(master=self,
                                  text="Switches / Destinations",
                                  fg_color="gray30",
                                  corner_radius=6)

        self.title.grid(column=0, padx=10, pady=(10, 0), sticky="ew")

    # This method returns the ID from the current client we are handling. This is
    # used in part I.
    def return_current_ID(self):
        return self._current_ID

    # Part II.C: This function is for handling the changing of the clients
    # when a button from "Switch/Destination" is pressed. This method basically
    # changes the current client and updates it for part III.
    def set_current_client(self, client_id):
        # sets the current_ID variable to the client's ID we are handling
        self._current_ID = client_id
        # retrieve the data from the _client_dct from part I
        self._current_client = self._client_dct[self._current_ID]

        # Temp variable
        f_clk = True
        obj_ind = 0

        # Loops through the first click array and check
        # for if the current device we are handling is on the
        # "first click" state
        for index, i in enumerate(self._first_click_tracker):
            if i[0] == client_id:
                f_clk = i[1]
                obj_ind = index

        # If it is on first click, remove it out of that state
        if f_clk:
            self._first_click_tracker[obj_ind][1] = False

        # Update information through the data frame or Part III
        self._data_frame.update_client_ID(self._current_client,
                                          self._client_dct,
                                          f_clk)

    # Part II.B: This method adds newly arrived clients and creates a button
    # It uses dictionaries to quickly search for the ID.
    def add_client_button(self, c_dict):
        global Type_Change
        global MAC_2_IP_ID_CLR

        client_information = copy.copy(c_dict)
        clientID = client_information["ID"]
        clientMAC = client_information["MAC"]

        # Final check to make sure that the ID is new
        if clientID not in self._client_dct:
            # Creating the button and setting its colors
            btn = ctk.CTkButton(master=self,
                                corner_radius=6,
                                fg_color=MAC_2_IP_ID_CLR[clientMAC]["Color"])

            # Spawns in with the right type
            if Type_Change[0] == 0:
                btn.configure(text=f"{clientID}")
            elif Type_Change[0] == 1:
                btn.configure(text=f"{clientMAC}")
            elif Type_Change[0] == 2:
                clientIP = MAC_2_IP_ID_CLR[clientMAC]["IP"]
                btn.configure(text=f"{clientIP}")

            # Makes sure the shape is uniformed like is correct
            btn.grid(column=0, padx=10, pady=(10, 0), sticky="ew")

            '''
            This is an anonymous function
            lambda argument: expression
            Anon functions are nameless functions that are basically one lined functions 
            that spits out a result once activated. This gives the button
            actual functionality. Every time this is clicked, set_current_client
            will run
            '''
            btn.configure(command=lambda x=clientID: self.set_current_client(x))

            # Add to part II's local dictionary
            self._client_btn[clientID] = btn
            self._client_dct[clientID] = {
                "ID": client_information["ID"],
                "MAC": client_information["MAC"],
                "IP": client_information["IP"],
                "Neighbor_Tuple": client_information["Neighbor_Tuple"],
                "XYZ_Tuple": client_information["XYZ_Tuple"]
            }
            # Make sure the condition is in the "first click"
            self._first_click_tracker.append([clientID, True])

    # This method deletes client button and clears it from the dictionary.
    # It is used by part I when a client drops.
    def del_client_button(self, client_information):
        self._current_ID = 0
        clientID = client_information["ID"]

        if clientID in self._client_btn:
            if self._client_btn[clientID]:
                self._client_btn[clientID].destroy()
                print(f"[{clientID}] has been deleted")

                del self._client_btn[clientID]

    # This method changes the type of this frame. It is used by part I.
    def change_type(self, _type, cd):
        client_dct = copy.copy(cd)
        for clientID in self._client_btn:
            # ID type
            if _type == 0:
                self._client_btn[clientID].configure(
                    text=clientID
                )
            # MAC type
            elif _type == 1:
                self._client_btn[clientID].configure(
                    text=client_dct[clientID]["MAC"]
                )
            # IP type
            elif _type == 2:
                self._client_btn[clientID].configure(
                    text=client_dct[clientID]["IP"]
                )

# Part I: This is the main class that handles all the incoming clients. Each client is treated as a thread
class PubSubGUI(ctk.CTk):
    # Part I.A: Default constructor
    def __init__(self, addr, port):
        super().__init__()
        global MAC_2_IP_ID_CLR
        # This library is to keep track of the IP, ID, and colors for easy access
        MAC_2_IP_ID_CLR[server_MAC] = {
            "IP": server_ADDR,
            "ID": "SERVER",
            "Color": "dark goldenrod"
        }

        self._ADDR = addr
        self._Port = port
        # This variable is for delay for if the current client is the server
        self._iterations = 1

        # GUI size adjustment
        self.title("Publish Subscribe WMN GUI")
        self.geometry("1100x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._client_dct = {}
        self._client_updated = {}

        # object for part III. This is the right frame of the GUI
        self.data_frame = DataFrame(self, self._client_dct)
        self.data_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # object for part II. This is the left side frame of the GUI. This frame determines
        # the current client ID that will be processed
        self.switch_frame = SwitchFrame(self, self.data_frame, self._client_dct)
        self.switch_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Initialization. The first node should ALWAYS be the server
        server_dict = {
            "ID": "SERVER",
            "MAC": server_MAC,
            "IP": server_ADDR,
            "Neighbor_Tuple": [False],
            "XYZ_Tuple": [False]
        }

        # Setting up the server for the switch frame. B/c the switch frame is empty to start
        self.switch_frame.add_client_button(server_dict)
        self.switch_frame.set_current_client("SERVER")

        # Starting the thread for part I.b and I.c
        time.sleep(0.01)
        BAT_server = threading.Thread(target=self.BATMAN_server_handler, args=())
        BAT_server.start()

        # Starting part I.D
        time.sleep(0.01)
        self.client_frames_handler()

    # Method for retrieving Batman IV information from the GUI host device
    def request_server_neighbors(self):
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
                                neigh_mac.append([current_location, next_hop])

                            neigh_LQ.append(link_quality)

            return neigh_mac, neigh_LQ

        except Exception as e:
            print(f"Error trying to get BAT info: {e}")
            return None

    # Part I.D: this is the section that handles updating the data frame from part III
    # this is the bridge for transmitting data between part I and part III
    def client_frames_handler(self):
        # Ask what the current ID is from part II
        current_client_ID = self.switch_frame.return_current_ID()

        # For if the current ID is the device hosting the GUI, begin updating.
        # Note, this update process has a delay of 4 iterations or 1 whole second
        if current_client_ID == "SERVER" and self._iterations >= 4:
            self._iterations = 0
            # If device requests Batman IV information
            if self._client_dct[current_client_ID]["Neighbor_Tuple"][0]:
                # Retrieves the data
                local_mac, local_lq = self.request_server_neighbors()
                device_neighbors = {
                    "nMAC": local_mac,
                    "LQ": local_lq
                }
                # Update the dictionary for the Batman IV information
                self._client_dct[current_client_ID]["Neighbor_Tuple"] = [
                    True,
                    device_neighbors
                ]
            else:
                # Otherwise keep the dictionary as false
                self._client_dct[current_client_ID]["Neighbor_Tuple"] = [False]

            # If the device requests drone location data
            if self._client_dct[current_client_ID]["XYZ_Tuple"][0]:
                device_xyz = {
                    "x": gen_random_number(0, 999),
                    "y": gen_random_number(0, 999),
                    "z": gen_random_number(0, 999)
                }

                # Update the dictionary for the drone location
                self._client_dct[current_client_ID]["XYZ_Tuple"] = [
                    True,
                    device_xyz
                ]
            else:
                # Otherwise keep the dictionary as false
                self._client_dct[current_client_ID]["XYZ_Tuple"] = [False]

            # After the dictionary is updated, begin updating the data frame from part III
            # update the neighbor data
            self.data_frame.display_neighbor(
                self._client_dct[current_client_ID]["Neighbor_Tuple"],
                current_client_ID
            )

            # Update the XYZ data
            self.data_frame.display_XYZ(
                self._client_dct[current_client_ID]["XYZ_Tuple"],
                current_client_ID
            )

            # Update the type in the switch frame. Note, Type_Change is a
            # variable that determines the type of data that will be displayed
            # such as ID, MAC, and IP. This is implemented in part III.
            if Type_Change[1]:
                # Tell the switch frame to change its type
                self.switch_frame.change_type(
                    Type_Change[0],
                    self._client_dct
                )
                Type_Change[1] = False
        # For if the current client we are handling is the other hosts
        elif current_client_ID in self._client_dct:
            if current_client_ID in self._client_updated:
                # Updating the client neighbor information and the XYZ
                if self._client_updated[current_client_ID]["updated"]:
                    # Update the neighbor data
                    self.data_frame.display_neighbor(
                        self._client_dct[current_client_ID]["Neighbor_Tuple"],
                        current_client_ID
                    )
                    # Update the XYZ data
                    self.data_frame.display_XYZ(
                        self._client_dct[current_client_ID]["XYZ_Tuple"],
                        current_client_ID
                    )
                    self._client_updated[current_client_ID]["updated"] = False

                # Update the type in the switch frame. Note, Type_Change is a
                # variable that determines the type of data that will be displayed
                # such as ID, MAC, and IP. This is implemented in part III.
                if Type_Change[1]:
                    self.switch_frame.change_type(
                        Type_Change[0],
                        self._client_dct
                    )

                    Type_Change[1] = False
        else:
            # You are on a host, and it disconnects, GUI will automatically
            # make the host computer as the default host.
            self.switch_frame.set_current_client("SERVER")

        # Make sure for the server it refreshes its data every 1 second
        self._iterations = self._iterations + 1
        # This is used to tell the CTKinter engine to refresh every 250 ms
        self.after(250, self.client_frames_handler)

    # Simple print function used for debugging
    def print_client_dct(self, client_id):
        print(f"From main - {client_id}")
        for clientID, sub_dict_client in self._client_dct.items():
            print(f"{clientID}: {sub_dict_client['Neighbor_Tuple']}")

    # Part I.C.a: updating the local database
    def update_client_dct(self, client_information):
        clientID = client_information["ID"]
        # Only update the database if the client ID is in the dictionary
        if clientID in self._client_dct:
            # These are booleans signifying if a request is made from the GUI and is
            # sent from the requester nodes
            server_neighbor_tuple = self._client_dct[clientID]["Neighbor_Tuple"][0]
            client_neighbor_tuple = client_information["Neighbor_Tuple"][0]
            server_XYZ_tuple = self._client_dct[clientID]["XYZ_Tuple"][0]
            client_XYZ_tuple = client_information["XYZ_Tuple"][0]

            # If both the client and server request conditions are true,
            # update the database
            if server_neighbor_tuple and client_neighbor_tuple:
                self._client_dct[clientID]["Neighbor_Tuple"] = copy.copy(client_information["Neighbor_Tuple"])
            if server_XYZ_tuple and client_XYZ_tuple:
                self._client_dct[clientID]["XYZ_Tuple"] = copy.copy(client_information["XYZ_Tuple"])

    # Part I.C: This is where each thread goes to be processed
    def BATMAN_Client_Handler_Thread(self, client_obj, addr):
        # This dictionary is for request handling
        data_req = {
            "Req_Neigh": False,
            "Req_XYZ": False
        }

        data_r = [False, False]
        first_connection = True
        bat_pack = {}
        currentID = 0
        bat_mac = ""

        try:
            # This while loop will only be active IFF the client is connected
            while True:
                # Checking for neighbors or XYZ conditions
                data = client_obj.recv(1024)

                # Decoding incoming packet
                bat_pack = json.loads(data.decode('utf-8'))
                currentID = bat_pack["ID"]

                # First connection handler
                if first_connection:
                    print(f"[{currentID}] has connected")
                    bat_mac = bat_pack["MAC"]

                    background_color = ""

                    # Gives host a background color
                    if len(color_list):
                        background_color = color_list[0]
                        color_list.pop(0)
                    else:
                        background_color = "gray30"

                    # Library for ease of access to colors
                    MAC_2_IP_ID_CLR[bat_mac] = {
                        "IP": bat_pack["IP"],
                        "ID": currentID,
                        "Color": background_color
                    }
                    self.switch_frame.add_client_button(bat_pack)
                    first_connection = False
                else:
                    print(f"[{currentID}] is sending information")
                    # If it is not a first connection, client dictionary is updated
                    self.update_client_dct(copy.copy(bat_pack))
                    time.sleep(0.001)
                    self._client_updated[currentID] = {
                        "updated": True
                    }

                # Request handling, checking our current dictionary if we need to ask
                # the client to send neighbor or XYZ data
                if self._client_dct[currentID]["Neighbor_Tuple"][0]:
                    data_r[0] = True
                else:
                    data_r[0] = False

                if self._client_dct[currentID]["XYZ_Tuple"][0]:
                    data_r[1] = True
                else:
                    data_r[1] = False

                # Sends dictionary request handler
                json_data = json.dumps(data_r)
                client_obj.sendall(json_data.encode('utf-8'))

                time.sleep(2)

        # Exception handling for a disconnection
        except Exception as e:
            print(f"Lost connection at {addr}: {e}")

        try:
            self.switch_frame.del_client_button(bat_pack)

        # Exception handling for an error with a button being deleted
        except Exception as e:
            print(f"Error deleting btn, client [{addr}]")

        # Removing client from local database in case of a disconnection
        if currentID in self._client_dct:
            del self._client_dct[currentID]

        if bat_mac in MAC_2_IP_ID_CLR:
            del MAC_2_IP_ID_CLR[bat_mac]

        # Thread close
        client_obj.close()

    # Part I.B: This is the main server socket that will create threads for each client connected
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

# Main function that starts everything
if __name__ == "__main__":
    # Creating the GUI object
    gui = PubSubGUI(server_ADDR, server_PORT)
    # b/c this is CTkinter, using mainloop() will loop through your GUI object thus
    # having a pseudo engine on
    gui.mainloop()
