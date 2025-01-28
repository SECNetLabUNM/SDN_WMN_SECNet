import customtkinter as ctk
import time
import socket as sck
import threading
import time as tm
import json

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class DataFrame(ctk.CTkFrame):
    def __init__(self, master, client):
        super().__init__(master)
        self.subscribe_state = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        paddingX = 20
        paddingY = 20

        self.title = ctk.CTkLabel(master=self, text="ID: NONE", fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=paddingX, pady=paddingY, sticky="w")

        self.sub_bt = ctk.CTkButton(master=self, text="Subscribe", command=self.subscribe_handler)
        self.sub_bt.grid(row=0, column=1, padx=0, pady=paddingY, sticky="w")

        self.unsub_bt = ctk.CTkButton(master=self, text="Unsubscribe", command=self.unsubscribe_handler)
        self.unsub_bt.grid(row=0, column=2, padx=paddingX, pady=paddingY, sticky="w")

    def update_client_ID(self, new_ID):
        self.title.configure(text=f"ID: {new_ID}")

    def subscribe_handler(self):
        return 1

    def unsubscribe_handler(self):
        return 1

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

    def button_action(self, client):
        self._data_frame.update_client_ID(client)

    def update_client_buttons(self, client):
        self._client = client
        # Clears old buttons
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkButton) and w != self.title:
                w.destroy()

        if len(self.client_btns) > 0:
            self.client_btns.clear()

        # Create new buttons
        index = 0
        for i in self._client:
            btn = ctk.CTkButton(master=self, text=f"{i}", corner_radius=6, command=lambda i=i: self.button_action(i))
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
        self.client = []
        self.client_btns = []
        self.updated_client_list = False

        BAT_server = threading.Thread(target=self.BATMAN_server_handler, args=())
        BAT_server.start()

        self.data_frame = DataFrame(self, self.client)
        self.data_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.switch_frame = SwitchFrame(self, self.data_frame)
        self.switch_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # This is the updater for all the data. It runs every 1 second
        self.update_GUI()

    def BATMAN_server_handler(self):
        # These values are for IPC, the server address is just the device address
        # Changing the port is not recommended but if you do change it, do it on the server side
        BAT_server_addr = "192.168.1.26"
        server_port = 1111
        GUI_client_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        holder_client = []
        while True:
            try:
                GUI_client_socket.connect((BAT_server_addr, server_port))
                while True:
                    data = GUI_client_socket.recv(1024)
                    if data:
                        info = json.loads(data.decode('utf-8'))
                        if holder_client != info:
                            holder_client = info
                            if holder_client != self.client:
                                self.client = holder_client
                                self.updated_client_list = True
                                print(self.client)
                        time.sleep(1)

            except sck.error:
                print(f"Error: {sck.error}")
                print(f"Retying to connect to server: {BAT_server_addr}")
                GUI_client_socket.close()
                tm.sleep(1)

    # This is for synchronization and updating parts of the GUI
    def update_GUI(self):
        if self.updated_client_list:
            self.switch_frame.update_client_buttons(self.client)
            self.updated_client_list = False
        self.after(250, self.update_GUI)

if __name__ == "__main__":
    gui = PubSubGUI()
    gui.mainloop()
