'''SimulationWindowWidgets are graphical elements insertable into simulation module 
graphicsViewWidget.\n
ParameterViewWidget can be used for text based information.\n
PictureViewWidget can be used for adding pictures.\n
spacerLine is used in ParameterViewWidget
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

# pylint: disable=E0611
# pylint: disable=E0401
import os
import numpy as np
import SimuMath
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtGui import QPixmap
import UtilityFunctions as uFunc


class spacerLine(QFrame):
    '''spacerLine is used to add horisontal line between 2 lines of text'''
    def __init__(self):
        super(spacerLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class ParameterViewWidget(QWidget):
    '''ParameterViewWidget is used for adding numerical update-able information to simulation\n
       graphicsViewWidget. Data is row based and inserted in call order.\n
       Each row has parameter name text, value and unit, which can be automatically handled.\n
       Can handle numbers in integer, decimal and complex forms. Complex numbers can be in\n
       rectangular or polar form. Numbers can be either user set, or update methods can be used\n
       for automatic formatting of numbers, including number of decimals and update of unit\n
       prefixes (micro, milli, kilo, mega...).
    '''
    def __init__(self, header:str, rounding:int=3):
        super().__init__()

        self.rounding_i = rounding
        self.physical_line_index = 2

        self.view_layout = QGridLayout()
        self.row_list = []
        self.unit_list = []
        self.spacer_line_list = []
        self.header = QLabel(self)
        self.header.setText(header)
        self.header.setMaximumHeight(20)

        self.view_layout.addWidget(self.header,0,0,1,3)
        self.setLayout(self.view_layout)


    def add_row(self, text:str, value, unit:str):
        '''Appends new row to list, with given text, value and unit'''
        new_line_num = len(self.row_list)
        self.row_list.append([])
        self.unit_list.append(unit)
        self.row_list[new_line_num].append(QLabel())
        self.row_list[new_line_num].append(QLabel())
        self.row_list[new_line_num].append(QLabel())

        self.row_list[new_line_num][0].setText(text)
        self.row_list[new_line_num][1].setText(str(round(value,self.rounding_i)))
        self.row_list[new_line_num][2].setText(unit)

        self.row_list[new_line_num][0].setMaximumHeight(20)
        self.row_list[new_line_num][1].setMaximumHeight(20)
        self.row_list[new_line_num][2].setMaximumHeight(20)

        self.view_layout.addWidget(self.row_list[new_line_num][0],self.physical_line_index,0,1,1)
        self.view_layout.addWidget(self.row_list[new_line_num][1],self.physical_line_index,1,1,1)
        self.view_layout.addWidget(self.row_list[new_line_num][2],self.physical_line_index,2,1,1)
        self.physical_line_index += 1

        self.setLayout(self.view_layout)


    def change_value(self, row:int, new_value):
        '''Changes the value of parameter at selected row to given new value'''
        self.row_list[row][1] = str(round(new_value,self.rounding_i))


    def update_row(self, row:int, new_value):
        '''Changes the value and unit power prefix at selected row according to the new value'''
        if new_value == 0:
            return
        dec = np.floor(np.log10(new_value))
        dec_pow = 0
        for i in range(0,4):
            if abs(dec-i) % 3 == 0:
                dec_pow = dec-i
                break
        self.row_list[row][2].setText(uFunc.unit_prefix(self.unit_list[row],
                                              dec_pow,
                                              dec_pow)[0])
        self.row_list[row][1].setText(str(round(new_value/(10**dec_pow),self.rounding_i)))


    def update_complex_row(self, row:int, new_value):
        '''Changes the value and unit power prefix at selected row according to the new value.
           Input as complex number in rectangular form'''
        real = np.real(new_value)
        imag = np.imag(new_value)
        if np.abs(imag) > np.abs(real):
            dec = np.floor(np.log10(np.abs(imag)))
        else:
            dec = np.floor(np.log10(real))
        dec_pow = 0
        for i in range(0,4):
            if abs(dec-i) % 3 == 0:
                dec_pow = dec-i
                break
        self.row_list[row][2].setText(uFunc.unit_prefix(self.unit_list[row],
                                              dec_pow,
                                              dec_pow)[0])
        if SimuMath.sign(imag) > 0:
            self.row_list[row][1].setText(str(round(real/(10**dec_pow),self.rounding_i))+
                                          " + j" +
                                          str(round(abs(imag)/(10**dec_pow),self.rounding_i)))
        else:
            self.row_list[row][1].setText(str(round(real/(10**dec_pow),self.rounding_i))+
                                          " - j" +
                                          str(round(abs(imag)/(10**dec_pow),self.rounding_i)))


    def update_polar_row(self, row:int, new_V, new_angle):
        '''Changes the value and unit power prefix at selected row according to the new value.
           Input as complex number in polar form'''
        dec = np.floor(np.log10(new_V))
        dec_pow = 0
        for i in range(0,4):
            if abs(dec-i) % 3 == 0:
                dec_pow = dec-i
                break
        self.row_list[row][2].setText(uFunc.unit_prefix(self.unit_list[row],
                                              dec_pow,
                                              dec_pow)[0])
        self.row_list[row][1].setText(str(round(new_V/(10**dec_pow),self.rounding_i))+"∠"+
                                      str(round(new_angle,1))+"°")


    def add_line(self):
        '''Add new spacer line at the end of the widget'''
        new_line_num = len(self.spacer_line_list)
        self.spacer_line_list.append(spacerLine())
        self.spacer_line_list[new_line_num].setMaximumHeight(3)
        self.spacer_line_list[new_line_num].setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.view_layout.addWidget(self.spacer_line_list[new_line_num],
                                   self.physical_line_index,0,1,3)
        self.physical_line_index += 1

        self.setLayout(self.view_layout)



class PictureViewWidget(QWidget):
    '''PictureViewWidget is used for adding pictures to simulation graphicsViewWidget.\n
       Pictures are added as is form given source.\n
       Default filelocation is in the simulator directory ./Simulation_files/Pictures.\n
       Directory formatting differences between Linuxand widows can be handled.
    '''
    def __init__(self, picture_name:str,
                 header:str="",
                 picture_directory:str='./Simulation_files/Pictures'):
        super().__init__()

        path = os.path.realpath(__file__)[:-len(os.path.basename(__file__))]

        self.picture_layout = QGridLayout()
        if "/" in path:
            self.picture = QLabel(pixmap=QPixmap(path + picture_directory + "/" + picture_name))
        else:
            self.picture = QLabel(pixmap=QPixmap(str(path + picture_directory + u"\U0000005C" + picture_name)))

        if header == "":
            self.picture_layout.addWidget(self.picture,0,0,1,1)
        else:
            self.header_label = QLabel(self,header)
            self.picture_layout.addWidget(self.header_label,0,0,1,1)
            self.picture_layout.addWidget(self.picture,1,0,100,1)

        self.setLayout(self.picture_layout)
