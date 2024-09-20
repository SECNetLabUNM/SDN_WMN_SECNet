On one device, create a server:
```
iperf -s 
```

On another device, do:
```
iperf -c <server ip>
```

tcpdump:
```
sudo tcpdump -i wlan0 -n port 4789
```
