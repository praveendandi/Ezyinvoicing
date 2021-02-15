import asyncio
import os,shlex
from subprocess import Popen, PIPE, STDOUT

def safe_decode(string, encoding='utf-8'):
    try:
        string = string.decode(encoding)
    except Exception:
        pass
    return string

def main():
    # test = os.popen("python -m ippserver --port 3000 save --pdf /home/caratred/Downloads/tmp/").read()
    commands = "python -m ippserver --port 3001 save --pdf /home/caratred/Downloads/tmp/"
    terminal = Popen(shlex.split(commands), stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = safe_decode(terminal.stdout.read(1))
    print(output)
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
# print("")
main()