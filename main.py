import gc
import multiprocessing
from gui.root import NewApp

# venv\Scripts\pyinstaller.exe --clean -w -F -i E:\GitHub\py3\GameProcessManager\media\icons\poker.ico -n ProcessManager main.py
if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = NewApp()
    app.MainLoop()
    gc.collect()
