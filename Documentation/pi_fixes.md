To use the internet certificate dates must be valid.
Set with `sudo date -s "<year><month><day> <hour (24 clock)>:<minute>MST"`

# Vncserver
1. Download RealVNCViewer on computer. On Pi run
2. `sudo raspi-config` then select (2) interface options > (I2) VNC > Yes
3. Vncserver is broken on 32 bit by default. See [here](https://github.com/raspberrypi/bookworm-feedback/issues/41)
Fix with
```sh
mkdir ~/delete_after_move
cd ~/delete_after_move

wget -nv https://github.com/raspberrypi/firmware/raw/master/opt/vc/lib/libbcm_host.so
wget -nv https://github.com/raspberrypi/firmware/raw/master/opt/vc/lib/libvcos.so
wget -nv https://github.com/raspberrypi/firmware/raw/master/opt/vc/lib/libmmal.so
wget -nv https://github.com/raspberrypi/firmware/raw/master/opt/vc/lib/libmmal_core.so
wget -nv https://github.com/raspberrypi/firmware/raw/master/opt/vc/lib/libmmal_components.so
wget -nv https://github.com/raspberrypi/firmware/raw/master/opt/vc/lib/libmmal_util.so
wget -nv https://github.com/raspberrypi/firmware/raw/master/opt/vc/lib/libmmal_vc_client.so
wget -nv https://github.com/raspberrypi/firmware/raw/master/opt/vc/lib/libvchiq_arm.so
wget -nv https://github.com/raspberrypi/firmware/raw/master/opt/vc/lib/libvcsm.so
wget -nv https://github.com/raspberrypi/firmware/raw/master/opt/vc/lib/libcontainers.so

sudo mv ~/delete_after_move/*.so /usr/lib/
cd ..
rmdir ~/delete_after_move

sudo systemctl restart vncserver-x11-serviced.service
```