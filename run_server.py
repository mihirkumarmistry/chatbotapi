import subprocess
import threading
import time
import os

def run_django():
    subprocess.call(["python", "manage.py", "runserver", "127.0.0.1:8000"])

def run_websocket():
    os.system("python websocket_server.py")

if __name__ == "__main__":
    t1 = threading.Thread(target=run_django)
    t2 = threading.Thread(target=run_websocket)

    t1.start()
    time.sleep(1)  # Let Django start first
    t2.start()

    t1.join()
    t2.join()
