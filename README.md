# Software Defined Network Functionalities on Wireless Mesh Network

This project aims to implement software defined networking (SDN) capabilities onto a wireless mesh network (WMN). It will take advantage of a WMN underlay network as the main routing back bone while there will be an SDN overlay networking running on top that will provide the typical suite of SDN functionalities. 

The project is built as a individual WMN enabled hosts communicating with each other via the BATMAN protocol. Each host will then become OpenFlow enabled, with one host serving as a SDN controller while the others will act as SDN enabled hosts with a virtual swtich.  Included is a custom GUI that can request the following information from each SDN host: Batman IV link quality, and drone location (in progress).

This repository is tied to a thesis paper that will have a much more thorough explanation of how every piece works together, what software and hardware were chosen and the justifications why. 

### Software Used
This project uses Better Approach to Mobile Ad-hoc Networking (BATMAN) for the WMN, OpenFlow for SDN, and OpenVSwitch as the virtual SDN enabled switch. 

Because this project is meant to be implemented onto a drone network in the future, hardware switches are not an option. Virtualization of OpenFlow will be mandatory for this project.
### Hardware Used
We used Raspberry Pi 4's running 

### Recreating This Project



