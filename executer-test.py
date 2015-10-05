#Python

import sys
import subprocess
from subprocess import Popen, CREATE_NEW_CONSOLE

## test file, not working as intended

with open("server.py") as f:
    code = compile(f.read(), "server.py", 'exec')
    exec(code)  # exec(code, global_vars, local_vars)
with open("client.py") as f:
    code = compile(f.read(), "client.py", 'exec')
    exec(code)  # exec(code, global_vars, local_vars)
    r = input("2nd>")
    exec(code)
'''
subprocess.Popen([sys.executable, 'server.py'], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
r = input("start>")
subprocess.Popen([sys.executable, 'client.py'], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
r = input("launch 2nd client>")
subprocess.Popen([sys.executable, 'client.py'], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
print ("starting")
r = input("exit>")
'''
