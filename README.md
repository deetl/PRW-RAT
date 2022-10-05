# PRW
PRW is a simple python-based RAT for educational purposes using WebSockets

# Motivation

Advanced Remote Administration tool for Windows Systems written in pure Python.

I really love the original work by [FZGbzuw412/Python-RAT](https://github.com/FZGbzuw412/Python-RAT)
for it's shortness and nice features. But I had **massive** problems due to the fixed buffer sizes for the communication pattern, especially when the answers became to large:

```
    def result(self):
        client.send(command.encode())
        result_output = client.recv(1024).decode()
        print(result_output)
```

So my first idea was just to change the code from simple socket usage to websockets (with execption of the streaming features). This whould make handling of sending and receiving messages much easier. Oh man, what was I thinking? A few small changes, I thought. Like such a newbie. The whole thing has now escalated into a complete rewrite starting from scratch. Let's see if this will work out now. 

## Warning

### DONT USE THE TOOL AT THE MOMENT! THIS IS WORK IN PROGRESS AND WILL NOT WORK! 

This software is for educational and [show hacking purposes](https://www.showhacking.de) only! Do not use it to harm anyone 
(and honestly, any virus scanner or EDR should blow this thing completely to pieces)! By 
using my application you automatically agree to all laws that apply to you and take responsibility 
for your actions! Violation of laws can have serious consequences! As the developer, I do not 
accept any liability and am not responsible for any misuse or damage caused by this program. 

## Target architecture

Client: Windows

Server: Windows or Linux 
