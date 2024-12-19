'''UtilityFunctions has some useful functions for simulator program in general'''


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

import json
import os
from datetime import datetime
from platform import system as plat_sys



def open_json_file(filename, file_location="./"):
    '''Open and load .json file, returns data in same format written in file'''
    try:
        with open(file_location + "/" + filename, encoding="utf-8") as file:
            json_data_struct = json.load(file)
    except FileNotFoundError:
        txt_log("json file import failed, file not found")
        return
    except Exception as error:
        txt_log("json file import failed" + str(error))
        return
    return json_data_struct


def write_json_file(filename, data_for_file, location="./"):
    '''write input data to given .json file'''
    with open(location+filename, 'w', encoding='utf-8') as file:
        json.dump(data_for_file, file, ensure_ascii=False, indent=4)
    txt_log("Write_json_file" + str(location) + str(filename))


def txt_log(log_text:str, filename_log:str = "log_file.txt"):
    '''Appends log file (.txt) with given text'''
    path = os.path.realpath(__file__)[:-len(os.path.basename(__file__))]
    full_path = path+filename_log
    log_time = datetime.now()
    line = str(log_time) + "   >>>   " + log_text
    with open(full_path, 'a', encoding="utf-8") as file_txt:
        file_txt.write(str(line))
        file_txt.write('\n')


def get_os():
    '''Returns current operating system'''
    return plat_sys()


prefixes = ((12,"T"), (9,"G"), (6,"M"), (3,"k"),
                (0,""), (-3,"m"), (-6,"µ"), (-9,"n"), (-12,"p"))

def unit_prefix(unit:str="", minim:int=-6, maxim:int=6):
    '''Returns SI-unit multiplier prefix based on power of 10
    for example:
        in: unit=V"", minim=-3, maxim=3
        return [mV, V, kV]'''
    out = []
    for p in prefixes:
        if p[0] >= minim and p[0] <= maxim:
            out.append(p[1]+unit)
    return out


def resolve_unit_prefix(inp):
    '''Returns power of 10 based on SI-unit multiplier prefix
    for example: 
        in: µF/km
        return -6'''
    try:
        inp = inp[0]
    except IndexError:
        return 0
    for pref in prefixes:
        if inp == pref[1]:
            return pref[0]
    return 0
