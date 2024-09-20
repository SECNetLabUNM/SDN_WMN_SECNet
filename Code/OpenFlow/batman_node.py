import itertools
import json
import socket
import subprocess
from time import sleep
from typing import Literal

from config import CONTROLLER_IP, ID, PORT


def skip_past(item, s):
    """drop up to and including first match of item"""
    s = itertools.dropwhile(lambda x: x != item, s)
    s.__next__()  # and the item itself
    return s


def get_self_batman_addr() -> str:
    """Get local batman address as it appears in other nodes' neighbor output."""
    completed_process = subprocess.run(
        ["sudo", "batctl", "meshif", "bat0", "n"],
        capture_output=True,
        encoding="utf8",
    )

    # skip to start of address in command output
    s = completed_process.stdout.strip()
    s = skip_past("/", s)
    s = skip_past("/", s)
    # take only address not rest of output
    s = itertools.takewhile(lambda x: x != " ", s)
    return "".join(s)


def get_batman_table(table_id: Literal["oj", "nj"]):
    """Get the given batman debug table as json"""
    completed_process = subprocess.run(
        ["sudo", "batctl", "meshif", "bat0", table_id],
        capture_output=True,
        encoding="utf8",
    )
    return json.loads(completed_process.stdout.strip())


def get_self_switch_addr() -> str:
    """Get ipv4 address of the switch running on this node"""
    completed_process = subprocess.run(
        ["ip", "addr", "show", "bat0"],
        capture_output=True,
        encoding="utf8",
    )
    completed_process = subprocess.run(
        ["grep", "inet "],
        capture_output=True,
        encoding="utf8",
        input=completed_process.stdout,
    )
    s = skip_past(" ", completed_process.stdout.strip())
    # take only address not rest of output
    s = itertools.takewhile(lambda x: x != "/", s)
    return "".join(s)


def get_local_info_to_transmit() -> str:
    """Get all the info to transmit as a str"""
    out = {}
    out["neighbors"] = get_batman_table("nj")
    out["self"] = {}
    out["self"]["batman_addr"] = get_self_batman_addr()
    out["self"]["switch_addr"] = get_self_switch_addr()
    out["self"]["id"] = ID
    return json.dumps(out)


print(f"Example transmission: {get_local_info_to_transmit()}")

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    # send tables to controller every second
    while True:
        s.sendto(get_local_info_to_transmit().encode("utf8"), (CONTROLLER_IP, PORT))
        sleep(1)
