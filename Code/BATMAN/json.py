import json_parser
import subprocess

for i in range(50):
    completed_process = subprocess.run(["sudo", "batctl", "meshif", "bat0", "nj"], capture_output=True, encoding="utf8")
    data = json_parser.parse(completed_process.stdout)
    print(data)
