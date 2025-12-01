import os
import sys
import subprocess
import shutil
from pathlib import Path



def main():
    
    print("Запуск IDEF0 Editor - Pixel Perfect макет")

    from app import IDEF0App
    app = IDEF0App()
    app.run()


if __name__ == "__main__":
    main()