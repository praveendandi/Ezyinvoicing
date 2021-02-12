import asyncio
import os
import subprocess
from pyipp import IPP, Printer



async def main():
    test = os.popen("python -m ippserver --port 3000 save --pdf /home/caratred/Downloads/tmp/").read()
    print(test,"==============================")
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())