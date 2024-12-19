'''SimuMenu module contains objects MenuWidget, WarningDialog and function confirm_dialog.\n
MenuWidget contains the menu actions and methods for its operation.\n
WarningDialog object is used to for dialog windows with only one button.\n
confirm_dialog is used for dialog windows with positive and negative buttons.'''

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
import sys
import os
import subprocess
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar, QMessageBox, QWidgetAction, QSpinBox, QLabel
import UtilityFunctions



class MenuWidget(QMenuBar):
    def __init__(self, parent, signals):
        super().__init__()

        self.signals = signals
        self.control_signals = parent.simulation_control_signals
        self.take_step = parent.take_step
        self.open_simulation = parent.open_simulation
        self.close_simulation = parent.close_simulation
        self.simu_open = parent.simulation_open
        self.simu_speed_list = parent.simulation_speed_limits

        self.open_simu_filename = ""

        # File -menu
        self.file_menu = self.addMenu("File")
        self.file_menu.setToolTipsVisible(True)

        self.open_button_action = QAction("Open", self)
        self.open_button_action.setToolTip("Open new simulation, button not availble")
        self.open_button_action.triggered.connect(self.open_button_function)
        self.open_button_action.setEnabled(False)
        self.file_menu.addAction(self.open_button_action)
        self.close_button_action = QAction("Close", self)
        self.close_button_action.setEnabled(False)
        self.close_button_action.setToolTip("Close current simulation")
        self.close_button_action.triggered.connect(lambda: parent.close_simulation())
        self.file_menu.addAction(self.close_button_action)
        self.file_menu.addSeparator()

        self.export_submenu = self.file_menu.addMenu("Export")
        self.export_graph = QAction("Graph", self.export_submenu)
        self.export_graph.setToolTip("Export graph as jpeg, button not availble")
        self.export_graph.setEnabled(False)
        self.export_submenu.addAction(self.export_graph)
        self.export_data_data = QAction("Graph data", self.export_submenu)
        self.export_data_data.setToolTip("Export data shown in all graphs as .csv")
        self.export_data_data.setEnabled(False)
        self.export_submenu.addAction(self.export_data_data)
        self.export_data_full = QAction("Full data", self.export_submenu)
        self.export_data_full.setToolTip("Export full data as .csv")
        self.export_data_full.setEnabled(False)
        self.export_submenu.addAction(self.export_data_full)
        self.export_submenu.setEnabled(False)

        self.file_menu.addSeparator()

        self.settings_submenu = self.file_menu.addMenu("Settings")
        self.settings_submenu.setToolTip("Simulator settings")
        self.simu_speed_top = QWidgetAction(self)
        self.simu_speed_top_subwidget = QSpinBox(self)
        self.simu_speed_top_subwidget.setPrefix("Simulation speed max:   ")
        tt = "Simulation speed refers to frequency of step calculations.\n"
        tt += "Minimum and maximum values set the speed percentage 100 and 0 values\n"
        tt += "Different speeds can be set by user depending on computer\n"
        tt += "Maximum should not be set above 333 on Windows computers"
        self.simu_speed_top_subwidget.setToolTip(tt)
        self.simu_speed_top_subwidget.setRange(1/parent.simulation_speed_limits[0],1/0.001)
        self.simu_speed_top_subwidget.setValue(1/parent.simulation_speed_limits[1])
        self.simu_speed_top_subwidget.valueChanged.connect(
            lambda:self.simu_speed_setting_changed(1,self.simu_speed_top_subwidget.value()))
        self.simu_speed_top.setDefaultWidget(self.simu_speed_top_subwidget)
        self.simu_speed_bottom = QWidgetAction(self)
        self.simu_speed_bottom_subwidget = QSpinBox(self)
        self.simu_speed_bottom_subwidget.setPrefix("Simulation speed min:   ")
        self.simu_speed_bottom_subwidget.setToolTip(tt)
        self.simu_speed_bottom_subwidget.setRange(1,1/parent.simulation_speed_limits[1])
        self.simu_speed_bottom_subwidget.setValue(1/parent.simulation_speed_limits[0])
        self.simu_speed_bottom_subwidget.valueChanged.connect(
            lambda:self.simu_speed_setting_changed(0,self.simu_speed_bottom_subwidget.value()))
        self.simu_speed_bottom.setDefaultWidget(self.simu_speed_bottom_subwidget)
        self.settings_submenu.addAction(self.simu_speed_top)
        self.settings_submenu.addAction(self.simu_speed_bottom)
        self.save_settings_button = QAction(self)
        self.save_settings_button.setText("Save settings")
        tt = "Save settings to memory.\nSame values will be used in future"
        self.save_settings_button.setToolTip(tt)
        self.save_settings_button.triggered.connect(self.settings_save)
        self.settings_submenu.addAction(self.save_settings_button)

        self.file_menu.addSeparator()

        self.exit_button_action = QAction("Exit", self)
        self.exit_button_action.setToolTip("Exit program")
        self.exit_button_action.triggered.connect(lambda: self.exit_button_function(parent))
        self.file_menu.addAction(self.exit_button_action)

        #Simulation -menu
        self.simulation_menu = self.addMenu("Simulation")
        self.simulation_menu.setToolTipsVisible(True)

        self.start_button_action = QAction("Start", self)
        self.start_button_action.setToolTip("Starts/continues simulation")
        self.start_button_action.setEnabled(False)
        self.start_button_action.triggered.connect(lambda:self.start_clicked())
        self.simulation_menu.addAction(self.start_button_action)
        self.pause_button_action = QAction("Pause", self)
        self.pause_button_action.setToolTip("Pauses simulation")
        self.pause_button_action.setEnabled(False)
        self.pause_button_action.triggered.connect(lambda:self.pause_clicked())
        self.simulation_menu.addAction(self.pause_button_action)
        self.f_step_button_action = QAction("Step forward", self)
        self.f_step_button_action.setToolTip("Run simulation for one step.\n(grahed step)")
        self.f_step_button_action.setEnabled(False)
        self.f_step_button_action.triggered.connect(lambda:self.f_step_clicked())
        self.simulation_menu.addAction(self.f_step_button_action)
        self.simulation_menu.addSeparator()
        self.reset_button_action = QAction("Reset", self)
        tt = "Reset simulation to its default condition.\n"
        tt += "Includes simulation time set to 0 and all parameters"
        self.reset_button_action.setToolTip(tt)
        self.reset_button_action.setEnabled(False)
        self.reset_button_action.triggered.connect(lambda:self.simulation_reset_clicked())
        self.simulation_menu.addAction(self.reset_button_action)
        self.simulation_menu.addSeparator()

        self.adv_edit_enabled = False
        self.advanced_submenu = self.simulation_menu.addMenu("Advanced")
        self.advanced_edit = QAction("Advanced edit", self)
        tt = "Enable full parameter editing.\n"
        tt += "Editing of some simulation parameters are disabled, if changing them is not\n"
        tt += "part of designedtasks. This setting enables editing of said parameters."
        self.advanced_edit.setToolTip(tt)
        self.advanced_submenu.addAction(self.advanced_edit)
        self.advanced_edit.setEnabled(False)
        self.advanced_edit.triggered.connect(self.advanced_edit_clicked)
        self.plotting_interval = QWidgetAction(self)
        self.plotting_interval_subwidget = QSpinBox(self)
        self.plotting_interval_subwidget.setPrefix("Graphing interval:   ")
        tt = "Graphing interval value controls how often steps are plotted to graphs.\n"
        tt += "For example graphing value of 10 means that 1 in 10 computed steps are grawn "
        tt += "to graphs.\nThis is done to keep steptime low for computational accuracy, while"
        tt += " reducing load of drawing graphs.\nThis value can be increased or decreased by "
        tt += "the user depending on their computer power\nto achieve smooth graphing experience."
        self.plotting_interval_subwidget.setToolTip(tt)
        self.plotting_interval_subwidget.valueChanged.connect(
            lambda:signals.graphing_interval_change.emit(self.plotting_interval_subwidget.value()))
        self.plotting_interval.setDefaultWidget(self.plotting_interval_subwidget)
        self.advanced_submenu.addAction(self.plotting_interval)
        self.plotting_interval.setEnabled(False)

        self.steptime_top = QWidgetAction(self)
        self.steptime_sub = QLabel(self)
        self.steptime_sub.setText("Simulation step time: 0ms")
        self.steptime_top.setDefaultWidget(self.steptime_sub)
        self.simulation_menu.addAction(self.steptime_top)


        #View -menu
        self.view_menu = self.addMenu("View")
        self.view_menu.setToolTipsVisible(True)

        self.dock_button_action = QAction("Parameter edit", self)
        self.dock_button_action.setToolTip("Show parameter control if closed")
        self.dock_button_action.triggered.connect(lambda: parent.dock_widget.setVisible(True))
        self.view_menu.addAction(self.dock_button_action)

        #Help -menu
        self.hel_menu_menu = self.addMenu("Help")
        self.hel_menu_menu.setToolTipsVisible(True)

        self.manual_button_action = QAction("User manual", self)
        self.manual_button_action.setToolTip("Open simulator manual")
        self.manual_button_action.triggered.connect(lambda:self.open_pdf_manual("Main"))
        self.hel_menu_menu.addAction(self.manual_button_action)
        self.info_button_action = QAction("Simulation Info", self)
        self.info_button_action.setToolTip("Open simulation info sheet")
        self.info_button_action.triggered.connect(lambda:self.open_pdf_manual("Simulation"))
        self.info_button_action.setEnabled(False)
        self.hel_menu_menu.addAction(self.info_button_action)
        self.start_manu_button_action = QAction("Startup manual", self)
        self.start_manu_button_action.setToolTip("Open simulator startup manual")
        self.start_manu_button_action.triggered.connect(lambda:self.open_pdf_manual("Startup"))
        self.hel_menu_menu.addAction(self.start_manu_button_action)

    # File menu functions
    def open_button_function(self):
        '''New simulation opening -function,
           action location: SimuMenu.Widget -> self.file_menu -> open
        '''
        print("menu -> file -> Open was clicked")


    def exit_button_function(self, parent):
        '''Exit program -function,
           action location: SimuMenu.Widget -> self.file_menu -> Exit
        '''
        print("menu -> file -> Close was clicked")
        self.signals.continue_pause.emit(False)
        self.signals.terminate_computation.emit(True)
        if self.simu_open:
            message = "Simulation is open.\nAre you sure you want to close the program?"
        else:
            message = "Exit program?"
        exit_dialog = confirm_dialog("Exit", message, icon=QMessageBox.Question)
        if exit_dialog:
            print("Success!")
            try:
                parent.simulation_thread.terminate()
            except AttributeError:
                pass
            sys.exit()
        else:
            print("Cancel!")

    # Simulation menu functions
    def simulation_reset_clicked(self):
        '''Resets simulation when reset is clicked by closing and reopening the simulation'''
        self.signals.terminate_computation.emit(False)
        self.close_simulation()
        self.open_simulation(self.open_simu_filename)


    def start_clicked(self):
        """Control panel start button action"""
        print("start_pressed")
        self.signals.terminate_computation.emit(False)
        self.control_signals.continue_pause.emit(True)
        self.f_step_button_action.setEnabled(False)


    def pause_clicked(self):
        """Control panel pause button action"""
        print("pause_pressed")
        self.signals.terminate_computation.emit(True)
        self.control_signals.continue_pause.emit(False)
        self.f_step_button_action.setEnabled(True)


    def f_step_clicked(self):
        """Control panel forward step action"""
        print("forward_pressed")
        self.signals.terminate_computation.emit(False)
        self.take_step()


    def advanced_edit_clicked(self):
        '''Sends appropriate boolean signal when edvanced parameter edit button is clicked'''
        if not self.adv_edit_enabled:
            self.signals.allow_full_parameter_edit.emit(False)
            self.adv_edit_enabled = True
        else:
            self.signals.allow_full_parameter_edit.emit(True)
            self.adv_edit_enabled = False

    # View menu functions
    def enable_dock_button(self, inp):
        '''Enables or disables "parameters" button in View menu'''
        if inp:
            self.dock_button_action.setEnabled(False)
        else:
            self.dock_button_action.setEnabled(True)


    def simu_opened_closed(self, inp, filename, graphing_interv, steptime):
        '''Enables or disables buttons in menus'''
        self.close_button_action.setEnabled(inp)
        self.start_button_action.setEnabled(inp)
        self.pause_button_action.setEnabled(inp)
        self.f_step_button_action.setEnabled(inp)
        self.advanced_edit.setEnabled(inp)
        self.plotting_interval.setEnabled(inp)
        self.plotting_interval_subwidget.setValue(graphing_interv)
        self.info_button_action.setEnabled(inp)
        if inp:
            self.open_simu_filename = filename
            self.steptime_sub.setText("Simulation step time: "+ str(steptime*1000) +"ms")


    def simu_running_stopped(self,inp):
        '''Changes menu action enable states when simulation is set to run or stopped'''
        self.export_submenu.setEnabled(not inp)
        self.reset_button_action.setEnabled(not inp)
        self.open_button_action.setEnabled(not inp)
        self.close_button_action.setEnabled(not inp)
        self.f_step_button_action.setEnabled(not inp)
        self.plotting_interval_subwidget.setEnabled(not inp)
        self.simu_speed_top_subwidget.setEnabled(not inp)
        self.simu_speed_bottom_subwidget.setEnabled(not inp)
        self.save_settings_button.setEnabled(not inp)


    def simu_speed_setting_changed(self, button, value):
        '''Simulation speed setting change'''
        if button == 1:
            self.simu_speed_list[1] = round(1/value,4)
        else:
            self.simu_speed_list[0] = round(1/value,4)
        self.simu_speed_top_subwidget.setRange(1/self.simu_speed_list[0],1/0.001)
        self.simu_speed_bottom_subwidget.setRange(1,1/self.simu_speed_list[1])


    def settings_save(self):
        '''Saving settings to settings file'''
        path = os.path.realpath(__file__)[:-len(os.path.basename(__file__))]
        settings_dict = UtilityFunctions.open_json_file("settings.json",path)
        settings_dict["speed_timings"] = [round(1/self.simu_speed_bottom_subwidget.value(),4),
                                          round(1/self.simu_speed_top_subwidget.value(),4)]
        UtilityFunctions.write_json_file(filename="settings.json",
                                         data_for_file=settings_dict,
                                         location=path)


    def open_pdf_manual(self, file):
        '''Opens a pdf file in computers default pdf reader.
           Opened file depends on the input.'''
        path = os.path.realpath(__file__)[:-14-len(os.path.basename(__file__))]
        if file == "Startup":
            path += "Documents/Startup_manual.pdf"
        elif file == "Main":
            path += "Documents/Simulator_user_manual.pdf"
        elif self.open_simu_filename == "":
            return
        elif file == "Simulation":
            path += "Documents/"
            path += str(self.open_simu_filename)[:-3]
            path += "_manual.pdf"
        try:
            subprocess.call(["xdg-open", path])
        except Exception as error:
            UtilityFunctions.txt_log("Cannot open simulation manual > ", str(error))


class WarningDialog(QMessageBox):
    '''Popup with Ok button'''
    def __init__(self, parent, title="Warning", message="Warning message", icon=QMessageBox.NoIcon):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setStandardButtons(QMessageBox.Ok)
        self.setIcon(icon)
        self.setText(message)



def confirm_dialog(title="Confirm", message="Confirm message", icon=QMessageBox.NoIcon):
    '''Confimation dialog with "Yes" and "No" buttons.
       Returns True if Yes clicked and False if No clicked'''
    conf = QMessageBox()
    conf.setWindowTitle(title)
    conf.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    conf.setIcon(icon)
    conf.setText(message)

    selection = conf.exec()
    if selection == QMessageBox.Yes:
        return True
    else:
        return False
