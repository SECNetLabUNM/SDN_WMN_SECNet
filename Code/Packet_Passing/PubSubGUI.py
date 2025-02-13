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

client = []

# This is the data frame that is effected by the node switches (sub/unsub is here)
class DataFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.updated = False
        self.subscribeXYZ_pressed = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self._device_info = []
        self.state = []
        self.current_index = 0
        paddingX = 20
        paddingY = 20

        self.title = ctk.CTkLabel(master=self, text="ID: NONE", fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=paddingX, pady=paddingY, sticky="w")

        self.subXYZ_bt = ctk.CTkButton(master=self, text="Subscribe XYZ",
                                       fg_color="gray30", command=self.subscribeXYZ_handler)
        self.subXYZ_bt.grid(row=0, column=1, padx=0, pady=paddingY, sticky="w")

        self.clearXYZ_bt = ctk.CTkButton(master=self, text="Clear", command=self.clearXYZ_handler)
        self.clearXYZ_bt.grid(row=0, column=2, padx=paddingX, pady=paddingY, sticky="w")

        self.text_box = ctk.CTkFrame(master=self)
        self.text_box.grid(row=1, column=0, padx=paddingX, columnspan=4, sticky="we")

        # Dummy widget to control height
        self.text_label = ctk.CTkLabel(master=self.text_box, text="", height=35)  # Set the height you need
        self.text_label.pack(fill="both", expand=True)

    def contained(self, device_id):
        for i in self.state:
            if device_id in i:
                return True
        return False

    def update_client_ID(self, device_info):
        self._device_info = device_info
        self.updated = True
        for i, c in enumerate(client):
            if c[0] == self._device_info[0]:
                self.current_index = i
                break

        self.title.configure(text=f"ID: {self._device_info[0]}")
        self.update_widget_XYZ()

    # Client packet:
    # Index 0: device ID
    # Index 1: device neighbors
    # Index 2: device XYZ
    # Index 3: index when added, this will be changed on the server side
    def subscribeXYZ_handler(self):
        global client

        if not self.subscribeXYZ_pressed:
            self.subscribeXYZ_pressed = True
            client[self.current_index][2][0] = True
        else:
            self.subscribeXYZ_pressed = False
            client[self.current_index][2][0] = False

        # Making sure we do not click on an empty frame
        if len(self._device_info) > 0:
            self.update_widget_XYZ()

    def update_widget_XYZ(self):
        device_status = self._device_info[2][0]
        if device_status:
            self.subXYZ_bt.configure(fg_color=theme_green)
            self.text_label.configure(text=f"Subbed {self._device_info[0]}")
        else:
            self.subXYZ_bt.configure(fg_color="firebrick1")
            self.text_label.configure(text=f"Unsub {self._device_info[0]}")

    def return_device_state(self):
        return self._device_info

    def return_updates(self):
        if self.updated:
            self.updated = False
            return True
        else:
            return self.updated

    def clearXYZ_handler(self):
        self.text_label.configure(text=f"")

# This is the frame class of the switches / nodes themselves
class SwitchFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, data_frame):
        super().__init__(master)
        self._client = []
        self._data_frame = data_frame
        self.grid_columnconfigure(0, weight=1)
        self.title = ctk.CTkButton(master=self, text="B.A.T.M.A.N Switches", fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        self.client_btns = []

    def button_action(self, _client):
        self._data_frame.update_client_ID(_client)

    def update_client_buttons(self, _client_list):
        self._client = _client_list
        # Clears old buttons
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkButton) and w != self.title:
                w.destroy()

        if len(self.client_btns) > 0:
            self.client_btns.clear()

        # Create new buttons
        index = 0
        for i in self._client:
            btn = ctk.CTkButton(master=self, text=f"{i[0]}", corner_radius=6,
                                command=lambda i=i: self.button_action(i))
            btn.grid(row=index + 1, column=0, padx=10, pady=(10, 0), sticky="ew")
            self.client_btns.append(btn)
            index += 1


class PubSubGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Publish Subscribe WMN GUI")
        self.geometry("800x600")
        self.subscribed = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.client_btns = []
        self.updated_client_list = False
        self.updated_data_frame = False

        self.data_frame = DataFrame(self)
        self.data_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.switch_frame = SwitchFrame(self, self.data_frame)
        self.switch_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        time.sleep(0.1)
        BAT_server = threading.Thread(target=self.BATMAN_server_handler, args=())
        BAT_server.start()

    def overwrite_client_list(self, new_list):
        global client
        # if a button from the data frame was pressed, must check some conditions
        if self.data_frame.return_updates():
            return 1

        else:
            client = new_list

    def BATMAN_server_handler(self):
        global client
        # These values are for IPC, the server address is just the device address
        # Changing the port is not recommended but if you do change it, do it on the server side
        BAT_server_addr = get_local_ip()
        server_port = 1111
        GUI_client_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)

        while True:
            try:
                GUI_client_socket.connect((BAT_server_addr, server_port))
                while True:
                    # Receiver
                    data = GUI_client_socket.recv(1024)
                    info = json.loads(data.decode('utf-8'))
                    if info:
                        if len(client) == 0:
                            client = info
                            self.updated_client_list = True
                        else:
                            # If a list sent by controller len != self.client length,
                            # we know that something has been updated
                            if len(info) != len(client):
                                client = info
                                self.updated_client_list = True
                            # If it's the same length, have to check ID's
                            else:
                                non_match = False
                                for index, i_info in enumerate(info):
                                    if i_info[0] != client[index][0]:
                                        non_match = True
                                        break

                                if non_match:
                                    client = info
                                    self.updated_client_list = True

                                # This will iterate through the packet and check if the data
                                # is true, if it is fill in the information
                                for index, i_info in enumerate(info):
                                    if i_info[1][0] and client[index][1][0]:
                                        client[index][1] = i_info[1]
                                    if i_info[2][0] and client[index][2][0]:
                                        client[index][2] = i_info[2]

                    if self.updated_client_list:
                        # Update the buttons if needed
                        print("updated list")
                        self.switch_frame.update_client_buttons(client)
                        self.updated_client_list = False

                    # Sender
                    json_data = json.dumps(client)
                    GUI_client_socket.sendall(json_data.encode('utf-8'))

                    time.sleep(1)

            except sck.error:
                print(f"Error: {sck.error}")
                print(f"Retying to connect to server: {BAT_server_addr}")
                GUI_client_socket.close()
                tm.sleep(1)

if __name__ == "__main__":
    gui = PubSubGUI()
    gui.mainloop()
