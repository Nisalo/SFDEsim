'''MainViewWidget has the object StartUp object for simulation selection menu'''


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
import os
from inspect import getfile, currentframe
from functools import partial
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGridLayout, QWidget, QPushButton, QLabel)
from PySide6.QtGui import QFont
import UtilityFunctions



class StartUp(QWidget):
    '''StartUp widget is the main window at startup containing the simulation selection menu'''
    def __init__(self, parent):
        super().__init__()

        own_location = os.path.dirname(os.path.abspath(getfile(currentframe())))
        self.simulation_info = UtilityFunctions.open_json_file("Simulation_list.json",
                                                               own_location + "/Simulation_files")
        print(self.simulation_info["subjects"].keys())

        self.startup_layout = QGridLayout()
        self.startup_layout.setColumnMinimumWidth(0,250)
        self.startup_layout.setColumnStretch(0,250)
        self.startup_layout.setColumnMinimumWidth(1,50)
        self.startup_layout.setColumnStretch(1,50)
        self.startup_layout.setColumnMinimumWidth(2,500)
        self.startup_layout.setColumnStretch(2,500)

        i_row = 0
        self.title_label = QLabel()
        self.title_label.setText("SFDEsim Simulator")
        self.title_label.setStyleSheet("font-weight: bold")
        self.title_label.setFont(QFont('Times', 50))
        self.startup_layout.addWidget(self.title_label, i_row,0,1,2)

        self.subtitle_label_list = []
        self.subject_label_list = []
        self.subject_button_list = []
        self.subject_description_list = []
        i_subj = -1
        i_simu = -1

        for subj in self.simulation_info["subjects"].keys():
            i_row += 1
            i_subj += 1
            self.subtitle_label_list.append(QLabel())
            self.subtitle_label_list[i_subj].setText(str(subj))
            self.subtitle_label_list[i_subj].setStyleSheet("font-weight: bold")
            self.subtitle_label_list[i_subj].setFont(QFont('Times', 24))
            self.startup_layout.addWidget(self.subtitle_label_list[i_subj], i_row,0)
            self.startup_layout.setRowStretch(i_row,0)

            for simu in self.simulation_info["subjects"][str(subj)].keys():
                i_row += 1
                i_simu += 1
                self.subject_label_list.append(QLabel())
                self.subject_label_list[i_simu].setText(str(simu))
                self.subject_label_list[i_simu].setFont(QFont('Times', 14))
                self.subject_label_list[i_simu].setAlignment(Qt.AlignLeft)
                self.startup_layout.addWidget(self.subject_label_list[i_simu], i_row,0)
                self.subject_button_list.append(QPushButton("Open"))
                self.subject_button_list[i_simu].clicked.connect(partial(parent.open_simulation,
                                                self.simulation_info["subjects"][str(subj)]
                                                [str(simu)]["filename"]))
                self.startup_layout.addWidget(self.subject_button_list[i_simu], i_row,1)
                self.startup_layout.setRowStretch(i_row,14)
                i_row += 1
                self.subject_description_list.append(QLabel())
                self.subject_description_list[i_simu].setText(self.simulation_info["subjects"]
                                                     [str(subj)][str(simu)]["abstract"])
                self.subject_description_list[i_simu].setFont(QFont('Times', 8))
                self.subject_description_list[i_simu].setAlignment(Qt.AlignLeft | Qt.AlignTop)
                self.startup_layout.addWidget(self.subject_description_list[i_simu], i_row,0)

        i_row += 1
        self.spacer_label = QLabel()
        self.spacer_label.setText(" ")
        self.spacer_label.setFont(QFont('Times', 14))
        self.startup_layout.addWidget(self.spacer_label, i_row,0)
        self.startup_layout.setRowStretch(i_row,14)
        self.spacer_label_row = i_row

        self.setLayout(self.startup_layout)
        self.spacer_label.update()


    def open_simu_clicked(self, inp):
        '''StartUp open simulation button clicked'''
        print("Open_clicked", inp)
