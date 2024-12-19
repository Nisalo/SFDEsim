'''SimulControlPanel has the controlpanel object'''


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
from PySide6.QtCore import  Slot
from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtWidgets import (QToolBar, QLabel, QCheckBox, QDoubleSpinBox, QPushButton)

bars = ["▰▱▱▱▱▱▱▱▱▱",
        "▱▰▱▱▱▱▱▱▱▱",
        "▱▱▰▱▱▱▱▱▱▱",
        "▱▱▱▰▱▱▱▱▱▱",
        "▱▱▱▱▰▱▱▱▱▱",
        "▱▱▱▱▱▰▱▱▱▱",
        "▱▱▱▱▱▱▰▱▱▱",
        "▱▱▱▱▱▱▱▰▱▱",
        "▱▱▱▱▱▱▱▱▰▱",
        "▱▱▱▱▱▱▱▱▱▰",
        "▱▱▱▱▱▱▱▱▰▱",
        "▱▱▱▱▱▱▱▰▱▱",
        "▱▱▱▱▱▱▰▱▱▱",
        "▱▱▱▱▱▰▱▱▱▱",
        "▱▱▱▱▰▱▱▱▱▱",
        "▱▱▱▰▱▱▱▱▱▱",
        "▱▱▰▱▱▱▱▱▱▱",
        "▱▰▱▱▱▱▱▱▱▱",
        ]


class Panel(QToolBar):
    '''Simulation control toolbar.
    Consists of simulation controls.'''
    def __init__(self, parent, control_signals, simu_open):
        super().__init__()

        self.control_signals = control_signals
        self.take_step = parent.take_step

        self.simulation_txt_label = QLabel()
        self.simulation_txt_label.setText("Simulation control:")
        self.addWidget(self.simulation_txt_label)

        # Main control buttons
        self.simu_contol_group = QActionGroup(self)

        self.start_simu_btn = QAction("Start", self)
        self.start_simu_btn.setCheckable(False)
        self.start_simu_btn.triggered.connect(lambda:self.start_pressed())
        self.simu_contol_group.addAction(self.start_simu_btn)
        self.addAction(self.start_simu_btn)

        self.pause_simu_btn = QAction("Pause", self)
        self.pause_simu_btn.setCheckable(False)
        self.pause_simu_btn.triggered.connect(lambda:self.pause_pressed())
        self.simu_contol_group.addAction(self.pause_simu_btn)
        self.addAction(self.pause_simu_btn)

        self.simu_contol_group.setEnabled(simu_open)

        self.addSeparator()
        self.separator_space_label1 = QLabel()
        self.separator_space_label1.setText("  ")
        self.addWidget(self.separator_space_label1)

        # Step buttons
        self.step_simu_contol_group = QActionGroup(self)

        self.f_step_simu_btn = QAction("Step >>", self)
        self.f_step_simu_btn.setCheckable(False)
        self.f_step_simu_btn.triggered.connect(self.f_step_pressed)
        self.step_simu_contol_group.addAction(self.f_step_simu_btn)
        self.addAction(self.f_step_simu_btn)

        self.step_simu_contol_group.setEnabled(simu_open)

        self.addSeparator()
        self.separator_space_label2 = QLabel()
        self.separator_space_label2.setText("  ")
        self.addWidget(self.separator_space_label2)

        #Speed control
        self.speed_txt_label = QLabel()
        self.speed_txt_label.setText("Speed:")
        self.addWidget(self.speed_txt_label)

        self.speed_entry_field = QDoubleSpinBox()
        self.speed_entry_field.setValue(75)
        self.speed_entry_field.setMaximum(100)
        self.speed_entry_field.setMinimum(0.1)
        self.speed_entry_field.setSingleStep(10)
        self.speed_entry_field.setSuffix(" %")
        self.speed_entry_field.setDecimals(1)
        self.speed_entry_field.valueChanged.connect(lambda: self.speed_change(parent,
                                                        self.speed_entry_field.value()))
        self.addWidget(self.speed_entry_field)

        self.speed_entry_field.setEnabled(simu_open)

        self.addSeparator()
        self.separator_space_label3 = QLabel()
        self.separator_space_label3.setText("  ")
        self.addWidget(self.separator_space_label3)

        #Accept control
        self.updating_checkbox = QCheckBox()
        self.updating_checkbox.setText("Autoupdate")
        self.updating_checkbox.stateChanged.connect(self.update_check_clicked)
        self.addWidget(self.updating_checkbox)
        self.separator_space_label4 = QLabel()
        self.separator_space_label4.setText("  ")
        self.addWidget(self.separator_space_label4)
        self.updating_btn = QPushButton()
        self.updating_btn.setText("Update")
        self.updating_btn.setCheckable(False)
        self.updating_btn.setEnabled(False)
        self.updating_btn.clicked.connect(lambda:control_signals.update_inputs.emit(True))
        self.addWidget(self.updating_btn)
        self.addSeparator()

        #Prograss Indicator
        self.update_spacing_index = 0
        self.update_speed = 5
        self.bar_index = 0
        self.bar_edge_l = QLabel()
        self.bar_edge_l.setText("  ｜")
        self.bar_edge_r = QLabel()
        self.bar_edge_r.setText("｜  ")
        self.addWidget(self.bar_edge_l)
        self.bar = QLabel()
        self.bar.setText("▱▱▱▱▱▱▱▱▱▱")
        self.addWidget(self.bar)
        self.addWidget(self.bar_edge_r)


    def start_pressed(self):
        """Control panel start button action"""
        print("start_pressed")
        self.control_signals.terminate_computation.emit(False)
        self.control_signals.continue_pause.emit(True)


    def pause_pressed(self):
        """Control panel pause button action"""
        print("pause_pressed")
        self.control_signals.continue_pause.emit(False)
        self.control_signals.terminate_computation.emit(True)


    def f_step_pressed(self):
        """Control panel forward step action"""
        print("forward_pressed")
        self.control_signals.terminate_computation.emit(False)
        self.take_step()


    def speed_change(self, parent, val):
        """Control panel speed change action"""
        print("speed_changed:", val)
        self.update_speed = val*0.1
        parent.simulation_speed_change(val*0.01)


    def simu_opened_closed(self, inp):
        '''Updates button eneble states when simulation is opened or closed'''
        self.simu_contol_group.setEnabled(inp)
        self.step_simu_contol_group.setEnabled(inp)
        self.speed_entry_field.setEnabled(inp)
        self.updating_btn.setEnabled(inp)


    def update_check_clicked(self):
        '''Updates "update" button enable state when autoupdate is changed'''
        if self.updating_checkbox.isChecked():
            self.updating_btn.setEnabled(False)
        else:
            self.updating_btn.setEnabled(True)


    def simu_running_stopped(self,inp):
        '''Changes menu action enable states when simulation is set to run or stopped'''
        self.f_step_simu_btn.setEnabled(not inp)


    @Slot(bool)
    def progress_bar(self,_):
        '''progress_bar slot ticks the progress bar to its next step when called'''
        if self.update_speed <= self.update_spacing_index:
            self.bar.setText(bars[self.bar_index])
            self.bar_index += 1
            if self.bar_index >= 17:
                self.bar_index = 0
            self.update_spacing_index = 0
        else:
            self.update_spacing_index += 1
