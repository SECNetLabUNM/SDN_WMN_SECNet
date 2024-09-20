Ryu is a python based SDN controller with API's that allows you to write a controller from scratch. However, it sucks to use. It's also discontinued so we are on our own for fixing stuff. 

### REQUIREMENTS
I recommend making a python environment for this before you install Ryu.

THERE IS A requirements.txt PROVIDED!!!!
```
Python 3.8.10 (Above versions like 3.10 will not work!!!)
Pip 20.0.2

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
```
I believe there is a wheel dependency in here but I forgot what it was. You'll have to wait for the pip install to error out to see what you need.

Refer to issues 169 in the ryu github issues

[Ryu Download Guide](https://ryu.readthedocs.io/en/latest/getting_started.html)
I recommend to install ryu from pip:
```
pip install ryu
```

You will see Ryu 4.34 in your pip freeze. However, this does not guarantee that it works. 

Then you must download the [git](https://github.com/faucetsdn/ryu) for the controller and additional programs.

Alternatively, you can download the git and install from there:
```
git clone https://github.com/faucetsdn/ryu.git
cd ryu
pip install .
```

### Testing Download
This is when you'll test if your download works:
```
ryu-manager app.py
```

The apps we will be using are located in
```
ryu/ryu/app/
```

For just the controller, we will be using simple_switch_13.py
```
ryu-manager simple_switch_13.py
```
NOTE: you must be in the ryu folder in order to use ryu-manager. I recommend you go to the app file path all the time because most of our applications are there.

### Rest API
This API allows you to give your switches flow entries from the controller. You must be running:
```
ryu-manager simple_switch_13.py ofctl_rest.py
```

[Rest API Documentation](https://ryu.readthedocs.io/en/latest/app/ofctl_rest.html)

Once you have both of those programs running, lets try out a command:
```
curl -X GET http://localhost:8080/stats/switches
```
This command will give you all the ID's of every switch you have connected to the controller. 

NOTE: You must running this on the same computer as the controller. Also, it will give you a really long ID.

### Running w/ Better GUI

You can run RYU with the default GUI but it's too bare bones. I recommend you use this GUI instead: [https://github.com/martimy/flowmanager](https://github.com/martimy/flowmanager)

To run:
```
ryu-manager --observe-links ~/flowmanager/flowmanager.py ryu.app.simple_switch_13
```

Online GUI Address: [http://localhost:8080/home/index.html](http://localhost:8080/home/index.html)