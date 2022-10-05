# Ignore this file, this is just a brain dump for me

## Web Sockets

https://www.piesocket.com/blog/python-websocket#google_vignette

## Command Line History

Maybe a command line history might be nice
https://stackoverflow.com/questions/15416054/command-line-in-python-with-history


## Separate tools for mouse and keyboard

https://github.com/jrsk23/Python-RAT

## Refactored Version with larger buffers and seperate constants

https://github.com/PM-95025/Python-RAT

## Shell zerlegen
>>> import shlex, subprocess
>>> command_line = raw_input()
/bin/vikings -input eggs.txt -output "spam spam.txt" -cmd "echo '$MONEY'"
>>> args = shlex.split(command_line)
>>> print args
['/bin/vikings', '-input', 'eggs.txt', '-output', 'spam spam.txt', '-cmd', "echo '$MONEY'"]
>>> p = subprocess.Popen(args) # Success!

# Autocomplete
http://pymotw.com/2/readline/


