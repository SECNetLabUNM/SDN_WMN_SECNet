import customtkinter as ctk
import threading as thread

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# This is the frame class of the switches / nodes themselves
class SwitchFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, client):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.title = ctk.CTkLabel(master=self, text="B.A.T.M.A.N Switches", fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        btnIter = 1
        self.switches_btn = []
        for i in client:
            btn = ctk.CTkButton(master=self, text=f"{i['ID']}")
            self.switches_btn.append(btn)

        for i in self.switches_btn:
            self.grid_rowconfigure(btnIter, weight=1)
            i.grid(row=btnIter, column=0, padx=10, pady=(10,0), sticky="ew")
            btnIter += 1




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

        self.title = ctk.CTkLabel(master=self, text="ID: 1234567891011", fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=paddingX, pady=paddingY, sticky="w")

        self.sub_bt = ctk.CTkButton(master=self, text="Subscribe", command=self.subscribe_handler)
        self.sub_bt.grid(row=0, column=1, padx=0, pady=paddingY, sticky="w")

        self.unsub_bt = ctk.CTkButton(master=self, text="Unsubscribe", command=self.unsubscribe_handler)
        self.unsub_bt.grid(row=0, column=2, padx=paddingX, pady=paddingY, sticky="w")

    def subscribe_handler(self):
        return 1

    def unsubscribe_handler(self):
        return 1

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
        device_info = {
            "ID": "012345678910",
            "MAC": "00:A0:C9:14:C8:29",
            "IP": "192.168.1.1",
            "nMAC": ["00:A0:C9:14:C8:30", "00:A0:C9:14:C8:31", "00:A0:C9:14:C8:32"],
            "LQ": "255"
        }
        device_info1 = {
            "ID": "912345678911",
            "MAC": "00:A0:C9:14:C8:29",
            "IP": "192.168.1.18",
            "nMAC": ["00:A0:C9:14:C8:30", "00:A0:C9:14:C8:31", "00:A0:C9:14:C8:32"],
            "LQ": "125"
        }
        self.client.append(device_info)
        self.client.append(device_info1)

        self.switch_frame = SwitchFrame(self, self.client)
        self.switch_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.data_frame = DataFrame(self, self.client)
        self.data_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")


if __name__ == "__main__":
    gui = PubSubGUI()
    gui.mainloop()
