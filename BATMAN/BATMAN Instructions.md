For our BATMAN installation, we used Ubuntu 20.04.06 LTS and Raspberry Pi OS (64-bit). We have confirmed that these two operating systems can run Batman IV and Batman V. 

The official BATMAN documentation can be referenced here:

[https://www.open-mesh.org/projects/batman-adv/wiki](https://www.open-mesh.org/projects/batman-adv/wiki)

## Installation of BATMAN
On a terminal, run:
<pre> sudo apt install batctl bridge-utils </pre>
To confirm it is installed correctly, run:
<pre> sudo modprobe batman-adv` </pre>
## Setup Script
After downloading BATMAN. Use this script courtesy of this Reddit article:

[https://www.reddit.com/r/darknetplan/comments/68s6jp/how_to_configure_batmanadv_on_the_raspberry_pi_3/?rdt=44892](https://www.reddit.com/r/darknetplan/comments/68s6jp/how_to_configure_batmanadv_on_the_raspberry_pi_3/?rdt=44892)


