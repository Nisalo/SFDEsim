'''
    SFDEsim simulator launching program.\n
    This is the launcher for the simulator.\n
    It tests if computer has all required modules are installed and can install them after user\n
    confirmation. If or after installation, the MainApp.pyw is launched.\n
    If this does not work, MainApp.pyw can be run directly from the subdirectory PythonModules
'''

## Licensing
'''
This file is part of SFDEsim.

SFDEsim is free software: you can redistribute it and/or modify it under the terms of the
 GNU General Public License as published by the Free Software Foundation, either version 3
   of the License, or (at your option) any later version.

SFDEsim is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
 even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
 See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with SFDEsim. 
If not, see <https://www.gnu.org/licenses/>.
'''

import sys
import os
import subprocess
import importlib
import importlib.util
from platform import system as plat_sys
from time import sleep

os_type = plat_sys()
if not os_type in ("Linux", "Windows"):
    print("Operating system not supported.")
    print("For support, contact course teacher for more infromation")

path = os.path.realpath(__file__)[:-len(os.path.basename(__file__))]

print("Starting simulator")
error_list = []

try:
    full_module_name = "PythonModules." + "MainApp"
    importlib.util.find_spec(full_module_name, package=None)
except ModuleNotFoundError:
    print("Simulator application missing\nExiting program")
    sleep(14)
    sys.exit()

try:
    import numpy
except ImportError:
    error_list.append("numpy")

try:
    import PySide6
except ImportError:
    error_list.append("PySide6")

try:
    import pyqtgraph
except ImportError:
    error_list.append("pyqtgraph")

def pip_install(os, lib):
    '''Installs pip packages using shell commands of used OS'''
    install_error = False
    if os == "Linux":
        try:
            subprocess.call([sys.executable, "python3", "-m", "pip", "install", lib])
        except Exception as e1:
            print("cannot install library:", lib, " >>> ", e1)
            install_error = True
    elif os == "Windows":
        try:
            subprocess.call([sys.executable, "-m", "pip", "install", lib])
        except Exception as e2:
            print("cannot install library:", lib, " >>> ", e2)
            install_error = True
    return install_error

if len(error_list) > 0:
    print("Following Python libraries missing")
    for _, lib in enumerate(error_list):
        print(lib)
    install_confirm = False
    install_error = False

    while not install_confirm:
        inp = input("Install libraries from pip [y/n]?")
        if inp in ("n", "N"):
            print("Cannot launch simulator without libraries\nExiting program")
            sleep(14)
            sys.exit()
        elif inp.lower() == "y" or inp.lower() == "yes":
            install_confirm = True
        else:
            print("Unknown command")

    for _, lib in enumerate(error_list):
        install_error = pip_install(os_type, lib)

    if install_error:
        print("Cannot launch simulator without libraries\nExiting program")
        sleep(14)
        sys.exit()

print("Launching simulator")

if os_type == "Linux":
    os.system("nohup python3 " + path + "PythonModules/MainApp.pyw &")
elif os_type == "Windows":
    print("start pythonw3 " + path + "MainApp.pyw")
    print("\n")
    print("This console window can now be closed after the simulator window has opened")
    print("If the simulator does not launch, see startup manual in Simulator/Documents folder")
    os.system('pythonw3 "' + path + 'PythonModules\MainApp.pyw"')

sleep(34.3)
sys.exit()
