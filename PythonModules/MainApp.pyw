'''MainApplication of the SFDEsim simulator
   This program can be used to launch the simulator if the launcher does not work.
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
try:
    from UtilityFunctions import txt_log
except ImportError:
    with open("log_file.txt", 'a', encoding="utf-8") as file_txt:
        file_txt.write("   >>>   txt_log import error")
        file_txt.write('\n')
import sys
import os
import time
import importlib
from inspect import getfile, currentframe
try:
    from PySide6.QtCore import (Qt, QObject, Signal, QThread, Slot)
    from PySide6.QtGui import QResizeEvent
    from PySide6.QtWidgets import (QApplication, QMainWindow, QDockWidget,
                                   QMessageBox, QScrollArea)
except ImportError as pyside_error:
    txt_log("PySide6 import error > " + pyside_error)
    sys.exit()
try:
    import MainViewWidget
    import SimuParameterWidget
    import SimuControlPanel
    import SimuMenu
    import UtilityFunctions
except ImportError as simoerror:
    txt_log("Simulator module import error > " + simoerror)
    sys.exit()



def import_simulations(parent):
    '''Import simulation modules given in the simulation_list.json.\n
       Returns a dict with module name as key'''
    simu_modul = {}
    module_fail_names = ""
    own_location = os.path.dirname(os.path.abspath(getfile(currentframe())))
    simulation_info = UtilityFunctions.open_json_file("Simulation_list.json",
                                            own_location + "/Simulation_files")
    for subj in simulation_info["subjects"].keys():
        for simu in simulation_info["subjects"][str(subj)].keys():
            module_name = simulation_info["subjects"][str(subj)][str(simu)]["filename"][0:-3]
            full_module_name = "Simulation_files." + str(module_name)
            try:
                simu_modul[str(module_name)] = importlib.import_module(full_module_name,
                                                                       package=None)
            except ModuleNotFoundError as error:
                module_fail_names += (str(module_name) + " (not found)" + "\n")
                UtilityFunctions.txt_log("Simulation import error, " + str(module_name)
                                         + " not found > " + str(error))
            except Exception as error:
                module_fail_names += (str(module_name) + " (error)" + "\n")
                UtilityFunctions.txt_log("Simulation import error " + str(module_name)
                                         + " general error > " + str(error))

    if len(module_fail_names) > 0:
        error_dialog = SimuMenu.WarningDialog(parent=parent,
                                title="Import error",
                                message="Import of simulation modules failed: \n \n"
                                + module_fail_names,
                                icon=QMessageBox.Warning)
        error_dialog.exec()
    return simu_modul



class SimuSignals(QObject):
    '''Simulationflow control signals'''
    start_run = Signal(bool)
    continue_pause = Signal(bool)
    step_data = Signal(list)
    update_inputs = Signal(bool)

    close_simulation = Signal(bool)
    allow_full_parameter_edit = Signal(bool)
    graphing_interval_change = Signal(int)

    simulation_error = Signal(list)
    terminate_computation = Signal(bool)

    update_progress_bar = Signal(bool)



class MainWindow(QMainWindow):
    default_aspect_ratio = [1280,720]
    location = os.path.dirname(os.path.abspath(getfile(currentframe())))
    def __init__(self):
        super().__init__()

        self.simu_modul = import_simulations(self)

        self.setWindowTitle("SFDEsim Simulator")
        app = QApplication.instance()
        screen = app.screenAt(self.pos())
        self.screen_geometry = screen.availableGeometry()
        self.resize(MainWindow.default_aspect_ratio[0],MainWindow.default_aspect_ratio[1])

        path = os.path.realpath(__file__)[:-len(os.path.basename(__file__))]
        try:
            self.settings_dict = UtilityFunctions.open_json_file("settings.json",path)
        except Exception as error_text:
            UtilityFunctions.txt_log("Settings read error > " + error_text)
            error_dialog = SimuMenu.WarningDialog(parent=self,
                        title="Settings error",
                        message="Cannot open settings file.\nUsing default values",
                        icon=QMessageBox.Warning)
            error_dialog.exec()
            self.settings_dict = {
                "speed_timings": [0.1, 0.0030]
                }

        self.simulation_control_signals = SimuSignals()
        self.simulation_control_signals.update_inputs.connect(self.update_inputs)
        self.simulation_control_signals.simulation_error.connect(self.show_error_message)
        self.simulation_open = False
        self.simulation_speed_limits = self.settings_dict["speed_timings"]
        self.simulation_delay = round(((self.simulation_speed_limits[0]-
                                       self.simulation_speed_limits[1])/4)*3,4)
        self.simulation_running = False
        self.terminate_computation = False
        self.open_simu_filename = ""
        self.simu_interval_step = 0
        self.start_graphing = False
        self.graphing_pause = False
        self.taking_step = False
        self.simu_graph_step_error = 0
        self.parameter_view_size = 240


        self.startup_menu_widget = MainViewWidget.StartUp(self)
        self.scroll_startup_menu_widget = QScrollArea(self)
        self.scroll_startup_menu_widget.setWidget(self.startup_menu_widget)
        self.scroll_startup_menu_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_startup_menu_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_startup_menu_widget.setWidgetResizable(False)
        self.setCentralWidget(self.scroll_startup_menu_widget)

        self.simu_control = SimuControlPanel.Panel(self,
                                                   self.simulation_control_signals,
                                                   self.simulation_open)
        self.addToolBar(self.simu_control)
        self.simulation_control_signals.update_progress_bar.connect(self.simu_control.progress_bar)

        self.menu_bar = SimuMenu.MenuWidget(self, self.simulation_control_signals)
        self.setMenuBar(self.menu_bar)

        self.dock_startup = SimuParameterWidget.StartUp(self)
        self.dock_widget = QDockWidget(self.tr("Parameter edit"), self)
        self.dock_widget.setWidget(self.dock_startup)
        self.dock_widget.setFloating(False)
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dock_widget.visibilityChanged.connect(self.menu_bar.enable_dock_button)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)



    def open_simulation(self, filename):
        '''Simulation opening fuction, initializes simulation objects and opens widgets'''
        UtilityFunctions.txt_log("opening simulation" + str(filename[0:-3]))
        self.open_simu_filename = filename

        #Simulation parameter object init
        try:
            self.parameter = self.simu_modul[str(filename[0:-3])].parameters()
        except Exception as error:
            txt_log("Simulation opening error > ", str(error))
            error_dialog = SimuMenu.WarningDialog(title="Simulation error",
                    message="Simulation you're trying to open ("+ str(error) +") is not imported",
                    parent=self,
                    icon=QMessageBox.Critical)
            error_dialog.exec()
            self.open_simu_filename = ""
            return

        self.simulation_control_signals.continue_pause.connect(self.simu_run_pause)
        self.simulation_control_signals.terminate_computation.emit(False)

        # simulator object initialization and threading
        self.simulation = self.simu_modul[str(filename[0:-3])].simulator(self,
                                                                self.parameter,
                                                                self.simulation_control_signals,
                                                                self.send_to_graph)
        self.simulation_thread = QThread()
        self.simulation_control_signals.start_run.connect(self.simulation.run)
        self.simulation.moveToThread(self.simulation_thread)
        self.simulation_thread.start()

        # simulator graphics object initialization
        self.simulation_view = self.simu_modul[str(filename[0:-3])].graphicsViewWidget(self,
                                                                        self.parameter,
                                                                        self.graphing_flow_control)
        self.simulation_control_signals.step_data.connect(self.simulation_view.update)
        self.setCentralWidget(self.simulation_view)

        self.simu_control.simu_opened_closed(True)
        self.menu_bar.simu_opened_closed(True,
                                         filename,
                                         self.parameter.graphing_interval,
                                         self.parameter.steptime)
        self.simulation_control_signals.graphing_interval_change.connect(self.change_graphing_interval)

        self.simulation_open = True

        self.simulation_control_signals.start_run.emit(False)

        self.parameter_view = SimuParameterWidget.SimuParameters(self,
                                                                 self.parameter.input_parameters)
        self.scroll_dock_widget = QScrollArea(self)
        self.scroll_dock_widget.setWidget(self.parameter_view)
        self.scroll_dock_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_dock_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_dock_widget.setWidgetResizable(False)
        self.dock_widget.setWidget(self.scroll_dock_widget)
        self.dock_widget.setMinimumWidth(self.parameter_view_size)
        self.simulation_control_signals.allow_full_parameter_edit.emit(not self.menu_bar.adv_edit_enabled)

        self.setWindowTitle("SFDEsim Simulator - " + self.parameter.simulation_name)



    def close_simulation(self):
        '''Simulation closing function, re-opens startUp widgets'''
        self.simulation_thread.terminate()
        self.startup_menu_widget = MainViewWidget.StartUp(self)
        self.scroll_startup_menu_widget = QScrollArea(self)
        self.scroll_startup_menu_widget.setWidget(self.startup_menu_widget)
        self.scroll_startup_menu_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_startup_menu_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_startup_menu_widget.setWidgetResizable(False)
        self.setCentralWidget(self.scroll_startup_menu_widget)

        self.dock_startup = SimuParameterWidget.StartUp(self)
        self.dock_widget.setWidget(self.dock_startup)
        self.dock_widget.setMinimumWidth(140)

        self.simu_control.simu_opened_closed(False)
        self.menu_bar.simu_opened_closed(False, "", 0, 0)
        self.simulation_open = False
        self.simu_graph_step_error = 0
        self.open_simu_filename = ""

        self.setWindowTitle("SFDEsim Simulator")


    @Slot(bool)
    def simu_run_pause(self, inp):
        '''Simulation pause slot, True input continues running simulation,
           False input pauses simulation'''
        self.simulation_running = inp
        self.menu_bar.simu_running_stopped(inp)
        self.simu_control.simu_running_stopped(inp)
        if inp:
            self.simulation_control_signals.start_run.emit(False)


    @Slot(bool)
    def update_inputs(self,inp):
        '''Simulation input value update. Slot input true when update is manual.
        When Signal received, loops through all input parameters and updates new values,
        lastly executes update_matrixes() method to update values into calculation matrixes
        or singular variables, and does variable update calculations'''
        i_num = 0       # index offset of input_varables
        i_text = 0      # index offset of input_texts
        no_pref = 0     # index offset for non-prefix inputs
        if self.simu_control.updating_checkbox.isChecked():     #if auto update is ON
            for i,val in enumerate(self.parameter_view.value_inputs):
                if self.parameter_view.type_list[i] == "number":
                    if i in set(self.parameter_view.prefix_indexes):
                        # Refix indexes holds which input indexes have prefix selector
                        pref_str = self.parameter_view.prefix_inputs[i-no_pref].currentText()
                        unit = (self.parameter.input_parameters
                                [list(self.parameter.input_parameters.keys())[i]]["unit"])
                        pref_val = UtilityFunctions.resolve_unit_prefix(pref_str.replace(unit,""))
                    else:
                        pref_val = 0
                        no_pref += 1
                    self.simulation.input_variables[i+i_num] = (val.value()*(10**pref_val))
                    i_text -= 1
                elif self.parameter_view.type_list[i] == "dropdown":
                    self.simulation.input_texts[i+i_text] = val.currentText()
                    i_num -= 1
                    no_pref += 1

            self.simulation.update_matrixes()

        else:                                                   #if auto update is off
            if inp:
                for i,val in enumerate(self.parameter_view.value_inputs):
                    if self.parameter_view.type_list[i] == "number":
                        if i in set(self.parameter_view.prefix_indexes):
                        # Refix indexes holds which input indexes have prefix selector
                            pref_str = self.parameter_view.prefix_inputs[i-no_pref].currentText()
                            unit = (self.parameter.input_parameters
                                    [list(self.parameter.input_parameters.keys())[i]]["unit"])
                            pref_val = UtilityFunctions.resolve_unit_prefix(pref_str.replace(unit,""))
                        else:
                            pref_val = 0
                            no_pref += 1
                        self.simulation.input_variables[i+i_num] = (val.value()*(10**pref_val))
                        i_text -= 1
                    elif self.parameter_view.type_list[i] == "dropdown":
                        self.simulation.input_texts[i+i_text] = val.currentText()
                        i_num -= 1
                        no_pref += 1

                self.simulation.update_matrixes()



    def take_step(self):
        '''Activates simulation for one graphing step.
        Simulation is set to run and paused by graphing_flow_control() when step has been drawn'''
        self.taking_step = True
        self.simu_run_pause(True)



    def simulation_speed_change(self, inp):
        '''Sets the simulation speed. \n
           Simulation speed is determined by relative percentage between preset\n
           maximum and minum speed speeds\n
           speed is implemetned as delay between simulation step calculations\n\n
           Input: int: speed precentage'''
        self.simulation_speed = inp
        delay = round((self.simulation_speed_limits[0]-self.simulation_speed_limits[1])*(1-inp),4)
        if inp < 0.01:
            delay *= 5
        if delay > self.simulation_speed_limits[0]:
            delay = self.simulation_speed_limits[0]
        elif delay < self.simulation_speed_limits[1]:
            delay = self.simulation_speed_limits[1]
        self.simulation_delay = delay



    def simulation_flow_control(self):
        '''Controls simulation flow, including pausing and speed.\n
           Must be included in simulation loop to avoid crashind due thread desychnronization.
           Pauses simulation calculations if 90 % of the graphing interval is reached before graphs
           are updated.'''
        self.parameter.simulation_time += self.parameter.steptime
        if self.start_graphing:
            if self.simu_interval_step >= 0.9*self.parameter.graphing_interval:
                self.simu_run_pause(False)
                self.graphing_pause = True
        if not self.simulation_running: # is this needed?
            time.sleep(0.25)
            return False
        time.sleep(self.simulation_delay)
        self.simulation_control_signals.update_progress_bar.emit(False)
        return True



    def send_to_graph(self, a_list:list):
        '''Auxilary simulation method, executed at the end of simulation slot to
        transfer computed data to graphs
        Input is a list consisting of varibles to be transfered to graphing Slot
        Acts as abstraction for simulation module.
        Only sends data to graph when graphing interval is reached'''
        self.simu_interval_step += 1
        if self.simu_interval_step >= self.parameter.graphing_interval:
            self.start_graphing = True
            self.simulation_control_signals.step_data.emit(a_list)
            self.simu_interval_step = 0



    def graphing_flow_control(self):
        '''Controls graphing flow, unlocks simulation if simulation_flow_control() has locked it
        for synchronicity.
        Pauses simulation if forward step has bee taken'''
        self.start_graphing = False
        if self.graphing_pause:
            self.simu_run_pause(True)
            self.graphing_pause = False
        if self.taking_step:
            self.taking_step = False
            self.simu_run_pause(False)


    @Slot(bool)
    def terminate_funct(self, inp):
        self.terminate_computation = inp



    def simulation_error(self, message:str):
        '''Pauses simulation and emits error message signal.\n
           Inteded to be used as simulation creator error function, for example in\n
           convergence error conditions'''
        self.simu_run_pause(False)
        UtilityFunctions.txt_log("Simulation error")
        title = "Simulation runtime error"
        self.simulation_control_signals.simulation_error.emit([message,title])


    @Slot(list)
    def show_error_message(self,message_title):
        '''Slot for error message which can be initiated from separate thread'''
        self.simulation_control_signals.continue_pause.emit(False)
        self.simu_run_pause(False)
        error_message = SimuMenu.WarningDialog(self,
                                title=message_title[1],
                                message=message_title[0],
                                icon=QMessageBox.Critical)
        error_message.exec()



    def closeEvent(self, event):
        '''Interrupts window closing from "X", if simulation is open confirms action'''
        self.simu_run_pause(False)
        self.simulation_control_signals.terminate_computation.emit(True)
        if not self.simulation_open:
            event.accept()
            return
        message = "Simulation is open.\nAre you sure you want to close the program?"
        confirm = SimuMenu.confirm_dialog(title="Warning",
                                         message=message,
                                         icon=QMessageBox.Warning)
        if confirm:
            self.simulation_thread.terminate()
            event.accept()
        else:
            event.ignore()



    def resizeEvent(self, event: QResizeEvent) -> None:
        '''MainWindow resize event, initializes graphing autoscale if used'''
        try:
            width = self.frameGeometry().width()
            height = self.frameGeometry().height()
            self.simulation_view.auto_scale(width, height)
        except BaseException:
            pass


    @Slot(int)
    def change_graphing_interval(self, new_interval):
        '''Change of graphing interval from menubar'''
        self.parameter.graphing_interval = new_interval



# Main app call
main_app = QApplication(sys.argv)

if __name__ == "__main__":
    main_win = MainWindow()
    main_win.show()
    main_app.exec()
