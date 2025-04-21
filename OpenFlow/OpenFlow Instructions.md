## Controller Installation
To run the controller, the minimum requirement we have found is `python 3.8` and `pip 20.0.2`. These are the python and pip3 versions we are using. Please create an environment that can run this python version. Below is our dependencies that are required for both the RYU controller.

<pre>
setuptools==44.0.0
eventlet==0.30.2
certifi==2023.7.22
charset-normalizer==3.3.0
debtcollector==2.5.0
dnspython==1.16.0
eventlet==0.31.1
greenlet==3.0.0
idna==3.4
msgpack==1.0.7
netaddr==0.9.0
oslo.config==9.2.0
oslo.i18n==6.1.0
ovs==3.1.2
packaging==20.9
pbr==5.11.1
pyparsing==3.1.1
PyYAML==6.0.1
repoze.lru==0.7
requests==2.31.0
rfc3986==2.0.0
Routes==2.5.1
six==1.16.0
sortedcontainers==2.4.0
stevedore==5.1.0
tinyrpc==1.0.4
urllib3==2.0.6
WebOb==1.8.7
wrapt==1.15.0
</pre>
With these dependencies installed, the RYU controller can be installed by running:

`pip install ryu`

Next, you must download the RYU GitHub provided below. 

[https://github.com/faucetsdn/ryu](https://github.com/faucetsdn/ryu)

If you want to download RYU from the GitHub, switch to this directory where you can either try the `setup.py` file or try `cd ryu; pip install .`. Note RYU is discontinued and the installation process can be frustrating. If there are any weird errors, the issues section of the RYU GitHub might provide some answers.

To confirm that RYU is working, move to the `/ryu/app` section and run `ryu-manager simple_switch_13.py`. We recommend only running `ryu-manager` within the RYU git folder itself. If there are no error messages, the controller is working. This will run a controller that is OpenFlow 1.3 enabled. Note, you can run multiple programs at once with different flags that you will see later on.

### RYU Upgraded GUI
Provided is a GitHub to an upgraded GUI that runs with the RYU controller. We recommend using this GUI as we use it within our implementation.

[https://github.com/martimy/flowmanager](https://github.com/martimy/flowmanager)

This GUI requires `eventlet==0.30.2` and RYU to be installed and running. To run this GUI, run this command 

```
ryu-manager --observe-links ~/flowmanager/flowmanager.py ryu.app.simple_switch_13
```
## Switch Installation