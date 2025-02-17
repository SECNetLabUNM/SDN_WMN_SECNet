import customtkinter as ctk
import time
import socket as sck
import threading
import time as tm
import json

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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
theme_green = "#2ca373"

# This is the data frame that is effected by the node switches (sub/unsub is here)
class DataFrame(ctk.CTkFrame):
    def __init__(self, master, client_dct):
        super().__init__(master)
        self._client_dct = client_dct
        self.temp_XYZ_text = {}
        self._current_device_info = {}
        self.subscribeXYZ_pressed = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1,)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        paddingX = 20
        paddingY = 20

        self.titleID = ctk.CTkLabel(master=self,
                                    text="ID: NONE",
                                    fg_color="gray30",
                                    corner_radius=6)

        self.titleID.grid(row=0, column=0, padx=(paddingX, 5), pady=paddingY, sticky="we")

        self.titleMAC = ctk.CTkLabel(master=self,
                                     text="MAC: NONE",
                                     fg_color="gray30",
                                     corner_radius=6)

        self.titleMAC.grid(row=0, column=1, padx=5, pady=paddingY, sticky="we")

        self.titleIP = ctk.CTkLabel(master=self,
                                    text="IP: NONE",
                                    fg_color="gray30",
                                    corner_radius=6)

        self.titleIP.grid(row=0, column=2, padx=(5, paddingX), pady=paddingY, sticky="we")

        self.subXYZ_bt = ctk.CTkButton(master=self,
                                       text="Request XYZ",
                                       fg_color="gray30",
                                       command=self.subscribeXYZ_handler)

        self.subXYZ_bt.grid(row=1, column=0, padx=(paddingX, 5), sticky="we")

        self.clearXYZ_bt = ctk.CTkButton(master=self,
                                         text="Clear XYZ",
                                         command=self.clearXYZ_handler)

        self.clearXYZ_bt.grid(row=1, column=1, padx=5, sticky="we")

        self.statusXYZ_bt = ctk.CTkLabel(master=self,
                                         text="Unsubscribed",
                                         fg_color="firebrick1",
                                         corner_radius=6)

        self.statusXYZ_bt.grid(row=1, column=2, padx=(5, paddingX), sticky="we")

        self.text_box = ctk.CTkFrame(master=self)
        self.text_box.grid(row=2, column=0, padx=paddingX, pady=paddingY, columnspan=4, sticky="we")

        # Dummy widget to control height
        self.text_label = ctk.CTkLabel(master=self.text_box, text="", height=35)  # Set the height you need
        self.text_label.pack(fill="both", expand=True)

    def print_client_dct(self):
        print("From data frame")
        for clientID, sub_dict_client in self._client_dct.items():
            print(f"{clientID}: {sub_dict_client['data']}")

    def update_client_ID(self, device_info, client_dct, first_click):
        if first_click:
            self.subscribeXYZ_pressed = False
            self.text_label.configure(text="")

        self._current_device_info = device_info
        self._client_dct = client_dct
        self.titleID.configure(text=f"ID: {self._current_device_info['ID']}")
        self.titleMAC.configure(text=f"MAC: {self._current_device_info['MAC']}")
        self.titleIP.configure(text=f"IP: {self._current_device_info['IP']}")
        self.update_widget_XYZ()

    def subscribeXYZ_handler(self):
        device_ID = self._current_device_info["ID"]
        if not self.subscribeXYZ_pressed:
            self.subscribeXYZ_pressed = True
            self._client_dct[device_ID]["data"]["XYZ_Tuple"][0] = True
        else:
            self.subscribeXYZ_pressed = False
            self._client_dct[device_ID]["data"]["XYZ_Tuple"] = [False]
        self.print_client_dct()

        self.update_widget_XYZ()

    def update_widget_XYZ(self):
        if self.subscribeXYZ_pressed:
            self.subXYZ_bt.configure(fg_color=theme_green)
            self.statusXYZ_bt.configure(text="Subscribed", fg_color=theme_green)
        else:
            self.subXYZ_bt.configure(fg_color="firebrick1")
            self.statusXYZ_bt.configure(text="Unsubscribed", fg_color="firebrick1")

        self.display_XYZ()

    def display_XYZ(self):
        if self._current_device_info:
            status = self._current_device_info["XYZ_Tuple"][0]
            has_data = len(self._current_device_info["XYZ_Tuple"])
            clientID = self._current_device_info["ID"]

            if status and (has_data > 1):
                self.temp_XYZ_text[clientID] = {"data": self._current_device_info['XYZ_Tuple'][1]}
                self.text_label.configure(text=f"{self.temp_XYZ_text[clientID]['data']}")
            elif not status:
                if len(self.temp_XYZ_text) > 0 and clientID in self.temp_XYZ_text:
                        self.text_label.configure(text=f"{self.temp_XYZ_text[clientID]['data']}")
                else:
                    self.text_label.configure(text=f"")
            print("From DISPLAY XYZ:")
            print(self.temp_XYZ_text)

    def clearXYZ_handler(self):
        self.text_label.configure(text=f"")

# This is the frame class of the switches / nodes themselves
# The left section with the green buttons
class SwitchFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, data_frame, client_dct):
        super().__init__(master)
        self._client_dct = client_dct
        self._data_frame = data_frame
        self._first_click_tracker = {}
        self.client_btn = {}
        self.grid_columnconfigure(0, weight=1)
        self.title = ctk.CTkButton(master=self, text="B.A.T.M.A.N Switches", fg_color="gray30", corner_radius=6)
        self.title.grid(column=0, padx=10, pady=(10, 0), sticky="ew")

    def button_action(self, client_id):
        client_data = self._client_dct[client_id]["data"]
        f_clk = self._first_click_tracker[client_id]["f_clk"]

        if f_clk:
            self._first_click_tracker[client_id]["f_clk"] = False

        self._data_frame.update_client_ID(client_data, self._client_dct, f_clk)

    # This method adds newly arrived clients and creates a button
    # It uses dictionaries to quickly search for the ID
    def add_client_button(self, client_information):
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
            btn.configure(command=lambda x=clientID: self.button_action(x))

            """ ATTENTION: This is how the dictionary is made """
            """ dict{"ID from the switch": "btn": the buttons, "data": data from switch} """
            """ client_dct[ID]["data"][your choice] """
            self.client_btn[clientID] = {"btn": btn}
            self._client_dct[clientID] = {"data": client_information}
            self._first_click_tracker[clientID] = {"f_clk": True}

    def update_client_button(self, client_information):
        clientID = client_information["ID"]

        if clientID in self._client_dct:
            server_neighbor_tuple = self._client_dct[clientID]["data"]["Neighbor_Tuple"][0]
            client_neighbor_tuple = client_information["Neighbor_Tuple"][0]
            server_XYZ_tuple = self._client_dct[clientID]["data"]["XYZ_Tuple"][0]
            client_XYZ_tuple = client_information["XYZ_Tuple"][0]

            if server_neighbor_tuple and client_neighbor_tuple:
                self._client_dct[clientID]["data"]["Neighbor_Tuple"] = client_information["Neighbor_Tuple"]
            elif not server_neighbor_tuple:
                self._client_dct[clientID]["data"]["Neighbor_Tuple"] = [False]
            if server_XYZ_tuple and client_XYZ_tuple:
                self._client_dct[clientID]["data"]["XYZ_Tuple"] = client_information["XYZ_Tuple"]
            elif not server_XYZ_tuple:
                self._client_dct[clientID]["data"]["XYZ_Tuple"] = [False]

        self._data_frame.display_XYZ()

    # This method deletes client button and clears it from the dictionary
    def del_client_button(self, client_information):
        clientID = client_information["ID"]

        if clientID in self.client_btn:
            self.client_btn[clientID]["btn"].destroy()
            del self.client_btn[clientID]["btn"]

class PubSubGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Publish Subscribe WMN GUI")
        self.geometry("800x600")
        self.subscribed = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.client_dct = {}
        self.updated_client_list = False
        self.updated_data_frame = False
        self.send_2_client = False

        self.data_frame = DataFrame(self, self.client_dct)
        self.data_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.switch_frame = SwitchFrame(self, self.data_frame, self.client_dct)
        self.switch_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        time.sleep(0.01)
        BAT_server = threading.Thread(target=self.BATMAN_server_handler, args=())
        BAT_server.start()

    def print_client_dct(self, client_ID):
        print(f"From main - {client_ID}")
        for clientID, sub_dict_client in self.client_dct.items():
            print(f"{clientID}: {sub_dict_client['data']}")

    def BATMAN_Client_Handler(self, client_obj, addr):
        # This will keep track of when the client is added
        data_req = {
            "Req_Neigh": False,
            "Req_XYZ": False
        }
        first_connection = True
        bat_pack = {}

        while True:
            # Checking for neighbors or XYZ conditions
            data = client_obj.recv(1024)
            if not data:
                print(f"Connection lost at {addr}")
                break
            else:
                bat_pack = json.loads(data.decode('utf-8'))
                currentID = bat_pack["ID"]

                if first_connection:
                    self.switch_frame.add_client_button(bat_pack)
                    first_connection = False
                else:
                    self.switch_frame.update_client_button(bat_pack)

                self.print_client_dct(bat_pack["ID"])

                if self.client_dct[currentID]["data"]["Neighbor_Tuple"][0]:
                    data_req["Req_Neigh"] = True
                else:
                    data_req["Req_Neigh"] = False

                if self.client_dct[currentID]["data"]["XYZ_Tuple"][0]:
                    data_req["Req_XYZ"] = True
                else:
                    data_req["Req_XYZ"] = False

                json_data = json.dumps(data_req)
                client_obj.sendall(json_data.encode('utf-8'))

                time.sleep(3)

        self.switch_frame.del_client_button(bat_pack)
        client_obj.close()

    def BATMAN_server_handler(self):
        server_ADDR = get_local_ip()
        server_PORT = 9559
        server_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        server_socket.bind((server_ADDR, server_PORT))
        server_socket.listen()

        # Handler for the connected client objects
        while True:
            client_obj, address = server_socket.accept()
            sub_thread = threading.Thread(target=self.BATMAN_Client_Handler,
                                          args=(client_obj, address))
            sub_thread.start()

if __name__ == "__main__":
    gui = PubSubGUI()
    gui.mainloop()
