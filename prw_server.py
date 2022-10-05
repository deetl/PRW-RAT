#!/usr/bin/python3

#Playground
import asyncio
import websockets
import json
import shlex
from pprint import pprint

async def handler(websocket, path):
    global stored_command
    global stored_executed
    global config_store

    direct_commands = ["SYSINFO",
                       "SYSTEMINFO",
                       "GET_LOCATION",
                       "GET_TIME",
                       "GET_MONITORS",
                       "GET_DRIVES",
                       "GET_CPU",
                       "GET_PID",
                       "GET_ENV",
                       "GET_LOGIN",
                       "GET_LOGIN",
                       "GET_NETSTAT",
                       "GET_ROUTING",
                       "GET_WINDOWS",
                       "GET_TASKS",
                       "EXIT"]


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
        # print(f'stored flag: {stored_executed}')
        # if stored_executed:
        #     print("Kein gespecihertes Kommando")
        # else:
        #     print("Gespreichertes Kommando")
        #     command = stored_command
        if stored_executed:
            valid_command = False
            while not valid_command:
                # Read Command from user
                cmdline = input('Command >>  ')
                args = shlex.split(cmdline)
                try:
                    cmd = args[0]
                    valid_command = True
                except:
                    print("Enter HELP to get info on possible commands!")
            # Some aliases
            if cmd.upper() == "LS":
                args[0]="DIR"

            if cmd.upper() == "CD":
                args.pop(0)
                if len(args) == 0:
                    args = ["."]
                command = ["CD", args]
            elif cmd.upper() == "PWD":
                command = ["CD", ["."]]
            else:
                direct_command=False
                for d_cmd in direct_commands:
                    if cmd.upper() == d_cmd:
                        command = [d_cmd, []]
                        direct_command = True
                if not direct_command:
                    command = ["SHELL", args]
            command_json = json.dumps(command)
            stored_executed=False
            stored_command=command_json
        else:
            command_json=stored_command



        # print('#################### Start to SEND ##############')
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
        stored_executed = True

        print(">>>> Response:")
        for line in answer[1]:
            print(line.rstrip())




# ############

global stored_command
global stored_executed

global config_store


stored_command=[]
stored_executed=True

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
