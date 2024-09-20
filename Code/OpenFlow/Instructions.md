# For running the batman controller/node combo:
- The `config.py` should be set with a unique uuid and any other changes needed.
- The `batman_controller.py` code should run with `ryu-manager <options...> batman_controller.py` on the device that should be the controller.
- The `batman_node.py` code should run on every node including the one running the `batman_controller.py` controller. Do this with `python batman_node.py`

# Misc

This portion is for the code of the OpenFlow scripts that lets the user interact with the rest API. Run it when the RYU controller and OpenVSwitch is running.

```
python3 main.py pushFlows.py totalSwitches.py
```