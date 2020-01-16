import gc
import multiprocessing
from gui.root import NewApp
import sys

# venv\Scripts\pyinstaller.exe -F -i E:\GitHub\py3\GameProcessManager\media\icons\poker.ico -n ProcessManager main.py
if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = NewApp()
    app.MainLoop()
    gc.collect()
