
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
import sys
import os
from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtWidgets import (QGridLayout, QWidget, QSizePolicy, QPushButton, QSlider, QLabel)
import numpy as np
parent_directory = os.path.abspath('../Z_DI_Simulator')
sys.path.append('..')
from LinePlotWidget import LinePlotWidget
from SimulationWindowWidgets import ParameterViewWidget, PictureViewWidget
from SimuMath import sign, angle_loop_rad, solve_2bus_NR, pol2cart



cable_list = {"---": [-1,-1],
              "Turkey (ACSR)": [0.655, 1.27*10**-6],
              "Swan (ACSR)": [0.412, 1.22*10**-6],
              "Sparrow (ACSR)": [0.259, 1.18*10**-6],
              "Robin (ACSR)": [0.206, 1.15*10**-6],
              "Raven (ACSR)": [0.163, 1.13*10**-6],
              "Pigeon (ACSR)": [0.103, 1.08*10**-6]
              }


class parameters():
    '''parameters object is used to declare and contain simualtion parameters and
       input vaiables.
       Required parameters: simulation_name, steptime, simulation_time, graphing_interval
       The input variables are declared in input_parameters dictionary.'''
    def __init__(self):

        self.simulation_name = "Short circuit simulation"
        self.steptime = 0.00005
        self.simulation_time = 0
        self.data_length = 50000000
        self.graphing_interval = 5     # graphs are only redrawn every xth step to reduce load


        self.input_parameters = {
            "u_in":{
                "display_name": "Input line voltage",
                "symbol": "U_i_n",
                "editable": True,
                "type": "number",
                "init_value": 20,
                "unit": "V",
                "default_prefix": 3,
                "prefix_limits": [0,3],
                "maximum": 150*(10**3),
                "minimum": 0
            },
            "line_length":{
                "display_name": "Line length",
                "symbol": "l_l_i_n_e",
                "editable": True,
                "type": "number",
                "init_value": 10.0,
                "unit": "km",
                "default_prefix": 0,
                "prefix_limits": [0,3],
                "maximum": 1000,
                "minimum": 0
            },
            "line_resistance":{
                "display_name": "Line resistance",
                "symbol": "R_l_i_n_e",
                "editable": True,
                "type": "number",
                "init_value": 0.337,
                "unit": "Ω/km",
                "default_prefix": 0,
                "prefix_limits": [-3,3],
                "maximum": 100,
                "minimum": 0
            },
            "line_inductance":{
                "display_name": "Line inductance",
                "symbol": "L_l_i_n_e",
                "editable": True,
                "type": "number",
                "init_value": 0.001136,
                "unit": "H/km",
                "default_prefix": 0,
                "prefix_limits": [-6,0],
                "maximum": 1,
                "minimum": 0
            },
            "fault_distance":{
                "display_name": "Fault distance",
                "symbol": "d_f_a_u_l_t",
                "editable": True,
                "type": "number",
                "init_value": 5,
                "unit": "km",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum": 1000,
                "minimum": 0
            },
            "load_power":{
                "display_name": "Load power",
                "symbol": "P_l_o_a_d",
                "editable": True,
                "type": "number",
                "init_value": 1,
                "unit": "W",
                "default_prefix": 6,
                "prefix_limits": [0,9],
                "maximum": 100*10**6,
                "minimum": 0
            },
            "load_cos_phi":{
                "display_name": "Load cos(φ)",
                "symbol": "",
                "editable": True,
                "type": "number",
                "init_value": 0.9,
                "unit": "°",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum": 1,
                "minimum": 0
            },
            "load_type":{
                "display_name": "Load type",
                "symbol": "",
                "editable": True,
                "type": "dropdown",
                "items": ["ind.", "cap."],
                "unit": ""
            },
            "frequency":{
                "display_name": "Frequency",
                "symbol": "f",
                "editable": False,
                "type": "number",
                "init_value": 50,
                "unit": "Hz",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum": 1000,
                "minimum": 0
            },
            "fault_resistance":{
                "display_name": "Fault resistance",
                "symbol": "R_k",
                "editable": False,
                "type": "number",
                "init_value": 0.001,
                "unit": "Ω",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum": 100,
                "minimum": 0
            },
            "fault_reactance":{
                "display_name": "Fault reactance",
                "symbol": "X_k",
                "editable": False,
                "type": "number",
                "init_value": 0.001,
                "unit": "Ω",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum": 1,
                "minimum": 0
            },
            "trans_reactance":{
                "display_name": "Transformer reactance",
                "symbol": "X_T",
                "editable": False,
                "type": "number",
                "init_value": 3.32,
                "unit": "Ω",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum": 100,
                "minimum": 0
            },
            "subtransient_longitudinal_reactance":{
                "display_name": "Subtransient longitudinal reactance",
                "symbol": "X_d''",
                "editable": False,
                "type": "number",
                "init_value": 0.914,
                "unit": "Ω",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum": 1000,
                "minimum": 0
            },
            "transient_longitudinal_reactance":{
                "display_name": "Transient longitudinal reactance",
                "symbol": "X_d'",
                "editable": False,
                "type": "number",
                "init_value": 1.767,
                "unit": "Ω",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum": 1000,
                "minimum": 0
            },
            "longitudinal_reactance":{
                "display_name": "Longitudinal reactance",
                "symbol": "X_d",
                "editable": False,
                "type": "number",
                "init_value": 9.522,
                "unit": "Ω",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum": 1000,
                "minimum": 0
            },
            "longitudinal_resistance":{
                "display_name": "Longitudinal resistance",
                "symbol": "R_d",
                "editable": False,
                "type": "number",
                "init_value": 0.0052,
                "unit": "Ω",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum": 1000,
                "minimum": 0
            },
            "subtransient_idle_time_constant":{
                "display_name": "Subtransient idle time constant",
                "symbol": "T_0''",
                "editable": False,
                "type": "number",
                "init_value": 0.059 * 10,
                "unit": "s",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum": 1000,
                "minimum": 0
            },
            "transient_idle_time_constant":{
                "display_name": "Transient idle time constant",
                "symbol": "T_0'",
                "editable": False,
                "type": "number",
                "init_value": 4.75 * 10,
                "unit": "s",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum":1000,
                "minimum": 0
            }
        }


class simulator(QObject):
    '''Main simulation object.
    Simulation varibles and matemathics are included in the methods of this object.
    By default the simulation includes methods:
    init: should contain variable definitions.
    update_matrixes: should contain computations for simulation varible changes.
    run (Slot): should contain the mathematics run every simulation step.
    The simulator object is executed in separate thread to enable paraller execution,
    with the GUI. 
    '''
    fault = False
    short_circuit_power = 208
    def __init__(self, parent, params, signals, send_to_graph):
        super().__init__()

        print("initilzing simulator: Reference frame simulation")
        ### Do not change ###
        self.params = params
        self.signals = signals
        self.flow_control = parent.simulation_flow_control
        self.send_to_graph = send_to_graph
        ### Do not change ###


        self.input_variables = np.array(
            [self.params.input_parameters["u_in"]["init_value"],#0
             self.params.input_parameters["line_length"]["init_value"],#1
             self.params.input_parameters["line_resistance"]["init_value"],#2
             self.params.input_parameters["line_inductance"]["init_value"],#3
             self.params.input_parameters["fault_distance"]["init_value"],#4,
             self.params.input_parameters["load_power"]["init_value"],#5
             self.params.input_parameters["load_cos_phi"]["init_value"],#6
             #advanced
             self.params.input_parameters["frequency"]["init_value"],#7
             self.params.input_parameters["fault_resistance"]["init_value"],#8
             self.params.input_parameters["fault_reactance"]["init_value"],#9
             self.params.input_parameters["trans_reactance"]["init_value"],#10
             self.params.input_parameters["subtransient_longitudinal_reactance"]["init_value"],#11
             self.params.input_parameters["transient_longitudinal_reactance"]["init_value"],#12
             self.params.input_parameters["longitudinal_reactance"]["init_value"],#13
             self.params.input_parameters["longitudinal_resistance"]["init_value"],#14
             self.params.input_parameters["subtransient_idle_time_constant"]["init_value"],#15
             self.params.input_parameters["transient_idle_time_constant"]["init_value"]
             ], dtype=float
        )

        i = 0
        for _, var in enumerate(self.params.input_parameters.keys()):
            if self.params.input_parameters[var]["type"] == "number":
                self.input_variables[i] *= 10**self.params.input_parameters[var]["default_prefix"]
                i += 1

        self.input_texts = [
             self.params.input_parameters["load_type"]["items"][0]
        ]

        s_short_circuit = (((13.8*10**3)**2)/
                            self.input_variables[11])
        setattr(simulator,"short_circuit_power",round(s_short_circuit*10**-6,-1))


        self.fault_time = 0
        self.fault_angles = [0,0,0]

        self.fault = False
        self.first_fault = True

        self.max_currents = [0,0,0]
        self.I_last = [0,0,0]
        self.I_last_n = [0,0,0]
        self.I_peaks = [0,0,0]
        self.zero_crossing = [True,True,True]
        self.updated = 0
        self.slow_update_time = 0
        self.fault_slowdown = False
        self.end_fault_slowdown = False
        self.new_steptime = 0
        self.fault_slowdown_multiplier = 0.1

        self.pi2 = 2*np.pi
        self.phase_angles = np.array([0,
                                     -2*np.pi/3,
                                     -4*np.pi/3],
                                     dtype=float)

        self.angle_steps = 0

        self.update_matrixes()



    def update_matrixes(self):
        '''Function is executed after updating inputs either by user clicking the update button,
           or by changing input varibles when autoupdate is on. 
           Additionally fun at startup.
           This fuction should include all calculations not necessary to run every cycle but after 
           user action.'''
        # Load power calculations
        self.P_load = self.input_variables[5]
        self.cos_phi_load = self.input_variables[6]
        self.Q_load = self.input_variables[5]*np.sin(np.cos(self.cos_phi_load))
        if self.cos_phi_load > 0:
            self.S_load = self.P_load+self.Q_load*1j
        else:
            self.S_load = self.P_load-self.Q_load*1j

        # parameters cahnged to better named ones
        # "d"letters afer "_"represent apostrofies, for example Xd_dd = Xd''
        self.frequency = self.input_variables[7]
        self.X_T = self.input_variables[10]
        self.Xd_dd = self.input_variables[11]
        self.Xd_d = self.input_variables[12]
        self.Xd = self.input_variables[13]
        self.Rd = self.input_variables[14]
        self.Taud0_dd = self.input_variables[15]
        self.Taud0_d = self.input_variables[16]

        self.updated = self.params.graphing_interval+1
        self.slow_update_interval = 1/self.frequency/6
        self.line_len = self.input_variables[1]
        self.line_len_fault = self.input_variables[4]
        self.omega = 2*np.pi*self.frequency
        self.x_line = self.omega*self.input_variables[3]

        self.Ung = 13.8*10**3
        self.Ung_ln = self.input_variables[0]/np.sqrt(3)
        self.Ung_ln_hat = self.Ung_ln*np.sqrt(2)
        self.Rk = self.input_variables[8]
        self.Xk = self.input_variables[9]

        self.S_k_min = (self.Ung**2)/self.Xd
        self.S_k = getattr(simulator,"short_circuit_power")*10**6
        self.Xd_dd_new = (self.Ung**2)/self.S_k
        self.Xd_ratio = self.Xd_dd/self.Xd_dd_new
        self.Xd_dd = self.Xd_dd/self.Xd_ratio
        self.Xd_d = self.Xd_d/self.Xd_ratio
        self.Xd = self.Xd/self.Xd_ratio
        self.Rd = self.Rd/self.Xd_ratio

        #reference change
        mu = (self.input_variables[0]/self.Ung)**2
        self.Xd_dd *= mu
        self.Xd_d *= mu
        self.Xd *= mu
        self.Rd *= mu

        #Line parameters
        self.R_line = self.line_len*self.input_variables[2]
        self.X_line = self.line_len*self.x_line

        # Pre fault line, transformer and generator impedances
        R_pre = self.R_line+self.Rk
        X_pre = self.X_line+self.Xk+self.X_T

        self.Z = R_pre+X_pre*1j
        self.Y = 0+0*1j

        # Voltage iteration for pre-fault conditions
        U2_guess = self.input_variables[0]
        delta_2 = -np.arcsin((self.P_load*np.imag(self.Z))/(self.input_variables[0]*U2_guess))

        S_vector = np.array([0.0, (self.S_load)*-1])
        U_vector = np.array([self.input_variables[0], self.input_variables[0]])

        U_vector = np.array(np.zeros((2,)),dtype=complex)
        U_vector[0] = self.input_variables[0]
        U_vector[1] = pol2cart(U2_guess,delta_2*0.1)[0]-pol2cart(U2_guess,delta_2*0.1)[1]*1j

        Y_00 = (1/self.Z)+(self.Y/2)
        Y_01 = -(1/self.Z)
        Y_bus = np.array([[Y_00,Y_01],[Y_01,Y_00]],dtype=complex)

        self.U_r = solve_2bus_NR(Y_bus,U_vector,S_vector,1,1000)

        if np.isnan(self.U_r):
            # Convergence error handling
            message = "Receiving end voltage calculation does not converge\n"
            message += "Selected power cannot be supplied with given grid voltage\n "
            message += "and line parameters"
            self.signals.simulation_error.emit([message,
                                                "Convergence error"])

        # Pre fault conditions
        self.I_total = np.conjugate(self.S_load/(np.sqrt(3)*self.U_r))
        self.Z_load = self.U_r/self.I_total
        self.R_load = np.real(self.Z_load)
        self.X_load = np.abs(np.imag(self.Z_load))

        # Line impedances during fault
        self.R_line_fault = self.line_len_fault*self.input_variables[2]
        self.X_line_fault = self.line_len_fault*self.x_line

        # Pre-fault total impedance and current amplitude and rms-value
        self.R_no_fault = self.R_line+self.R_load
        self.X_no_fault = self.X_line+self.X_load
        self.Z_no_fault = np.sqrt((self.R_no_fault**2)+(self.X_no_fault**2))
        self.I_hat_no_fault = self.Ung_ln_hat/self.Z_no_fault
        self.I_no_fault = self.Ung_ln/self.Z_no_fault

        # Short-cirtuit impedances
        self.R_fault = self.R_line_fault+self.Rk
        if self.R_fault <= 0:
            self.R_fault = 1*10**-15
        self.X_fault = self.X_line_fault+self.Xk+self.X_T
        if self.X_fault <= 0:
            self.X_fault = 1*10**-15
        self.Zk = np.sqrt(self.R_fault**2+self.X_fault**2)
        self.Phi_k = np.arctan(self.X_fault/self.R_fault)

        # Time constants
        self.Tau_dd = ((self.Xd_dd+self.X_fault)/(self.Xd_d+self.X_fault))*self.Taud0_dd
        self.Tau_d = ((self.Xd_d+self.X_fault)/(self.Xd+self.X_fault))*self.Taud0_d
        self.Tau = (self.Xd_dd+self.X_fault)/(self.omega*(self.R_fault+self.Rd))

        # Generator source voltages
        self.E_dd = self.Ung_ln+self.Xd_dd*self.I_no_fault
        self.E_d = self.Ung_ln+self.Xd_d*self.I_no_fault
        self.E = self.Ung_ln+self.Xd*self.I_no_fault

        # Short circuit current components
        self.Ik_dd = self.E_dd/np.sqrt((self.Rd+self.R_fault)**2+(self.Xd_dd+self.X_fault)**2)
        self.Ik_d = self.E_d/np.sqrt((self.Rd+self.R_fault)**2+(self.Xd_d+self.X_fault)**2)
        self.Ik = self.E/np.sqrt((self.Rd+self.R_fault)**2+(self.Xd+self.X_fault)**2)



    @Slot(bool)
    def run(self, _):
        '''Simulation calculation method. 
        This method shoud include simulation step calculation and method for sending data to graph.
        Calculation loop is run as long as simulation is set ON by user.
        Data is sent to the graph via self.send_to_graph() function which should be called at the
        end of the method. This fucntion takes 1 input type=list, which should contain all data to
        be send for graphs or other visual elements in graphicsViewWidget'''
        while self.flow_control():
            # Checks if fault has been activated. If True, shortenes the steptime for 0.02 s 
            if getattr(simulator,"fault"):
                self.fault = True
                self.new_steptime = self.params.steptime*self.fault_slowdown_multiplier
                self.params.steptime = self.new_steptime
                self.fault_slowdown = True
                self.updated = self.params.graphing_interval+1
                self.update_matrixes()
                setattr(simulator,"fault",False)

            # calculates the phase angels
            self.angle_steps = (self.pi2/((1/self.frequency)/self.params.steptime))
            self.phase_angles += self.angle_steps
            phase_angles_rad = [0,0,0]
            phase_angles_rad[0] = angle_loop_rad(self.phase_angles[0])
            phase_angles_rad[1] = angle_loop_rad(self.phase_angles[1])
            phase_angles_rad[2] = angle_loop_rad(self.phase_angles[2])


            I = [0,0,0]
            #self.update_long_graph = False

            if not self.fault:
                I[0] = self.I_hat_no_fault*np.cos(phase_angles_rad[0])
                I[1] = self.I_hat_no_fault*np.cos(phase_angles_rad[1])
                I[2] = self.I_hat_no_fault*np.cos(phase_angles_rad[2])
                # If short circuit has not been made, calculates the currents as they are
                # without fault
            else:
                if self.first_fault:
                    self.fault_angles = phase_angles_rad
                    self.first_fault = False
                    # At the first step with fault, fault_angles (alpha) angle is saved
                self.fault_time += self.params.steptime
                component_1 = (self.Ik_dd-self.Ik_d)*np.exp(-self.fault_time/self.Tau_dd)
                component_2 = (self.Ik_d-self.Ik)*np.exp(-self.fault_time/self.Tau_d)
                component_4 = self.Ik_dd*np.exp(-self.fault_time/self.Tau)
                omega_t = self.omega*self.fault_time
                component_1a = component_1*np.sin(omega_t+self.fault_angles[0]-self.Phi_k)
                component_2a = component_2*np.sin(omega_t+self.fault_angles[0]-self.Phi_k)
                component_3a = self.Ik*np.sin(omega_t+self.fault_angles[0]-self.Phi_k)
                component_4a = component_4*np.sin(self.fault_angles[0]+self.Phi_k)

                component_1b = component_1*np.sin(omega_t+self.fault_angles[1]-self.Phi_k)
                component_2b = component_2*np.sin(omega_t+self.fault_angles[1]-self.Phi_k)
                component_3b = self.Ik*np.sin(omega_t+self.fault_angles[1]-self.Phi_k)
                component_4b = component_4*np.sin(self.fault_angles[1]+self.Phi_k)

                component_1c = component_1*np.sin(omega_t+self.fault_angles[2]-self.Phi_k)
                component_2c = component_2*np.sin(omega_t+self.fault_angles[2]-self.Phi_k)
                component_3c = self.Ik*np.sin(omega_t+self.fault_angles[2]-self.Phi_k)
                component_4c = component_4*np.sin(self.fault_angles[2]+self.Phi_k)

                I[0] = np.sqrt(2)*(component_1a+component_2a+component_3a+component_4a)
                I[1] = np.sqrt(2)*(component_1b+component_2b+component_3b+component_4b)
                I[2] = np.sqrt(2)*(component_1c+component_2c+component_3c+component_4c)
                # Short cirtuit components are calculated for all phases and added together to get 
                # the fault current

                if self.fault_slowdown:
                    if self.fault_time > 0.005:
                        self.end_fault_slowdown = True
                        self.fault_slowdown = False
                        self.new_steptime = self.params.steptime*(1/self.fault_slowdown_multiplier)
                        self.params.steptime = self.new_steptime
                        self.updated = self.params.graphing_interval+1
                        # If short circuit has been going on more than 0.02 seconds, steptime is
                        # returned to the original

            self.pause_at_fault_time(0.5)

            # Saves the peaks/amplitudes of currents
            for i, num in enumerate(I):
                if np.abs(num) < np.abs(self.I_last[i]):
                    if self.zero_crossing[i]:
                        self.I_peaks[i] = np.abs(self.I_last[i])
                        self.zero_crossing[i] = False
                if not self.zero_crossing[i]:
                    if sign(num) != sign(self.I_last_n[i]):
                        self.zero_crossing[i] = True
                self.I_last[i] = np.abs(num)
                self.I_last_n[i] = num

            # gets the absolute values of maximum currents
            for i,val in enumerate(I):
                if np.abs(val) > self.max_currents[i]:
                    self.max_currents[i] = np.abs(val)

            self.slow_update_time += self.params.steptime
            if self.slow_update_time > self.slow_update_interval:
                self.slow_update_time = 0
                #self.update_long_graph = True

            if self.updated >= 0:
                self.updated -= 1

            self.send_to_graph([I,#0
                                self.max_currents,#1
                                self.I_peaks,#2
                                self.fault_time,#3
                                self.slow_update_interval,#4
                                self.updated,#5
                                self.fault_slowdown,#6
                                self.new_steptime,#7
                                self.end_fault_slowdown,#8
                                [self.Xd_dd, self.Xd_d, self.Xd, self.Rd, self.X_fault, self.R_fault]
                                ])


    def pause_at_fault_time(self, time):
        '''Pauses the simulation after given fault time'''
        if self.fault_time > time+(self.params.steptime/2):
            return
        if self.fault_time < time-(self.params.steptime/2):
            return
        self.signals.continue_pause.emit(False)



class graphicsViewWidget(QWidget):
    '''Simulation graphics containment widdget.
       This widget is placed as central widget in the window.
       The definition and placements of all visual objects should be done in __init__ method, 
       including graphs, pictures, variable views, buttons etc.
       The update Slot method is run once every graphing interval defined in parameter object
       and should contain updates of all visual objects'''
    def __init__(self, parent, params, graphing_flow_control):
        super().__init__()
        ### Do not change ###
        self.parameters = params
        self.graphing_flow_control = graphing_flow_control
        ### Do not change ###

        self.simulation_view_layout = QGridLayout()
        parent.parameter_view_size = 270

        self.current_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                              plot_step=self.parameters.graphing_interval,
                                              x_lenght=2000, enable_legend=True,
                                              x_name="time [s]", y_name="Current [A]")
        self.current_graph.add_plotline("Ia",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.current_graph.add_plotline("Ib",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="blue")
        self.current_graph.add_plotline("Ic",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.current_graph.set_text(title="System current")


        a = "<sub>" + "a" + "</sub>"
        b = "<sub>" + "b" + "</sub>"
        c = "<sub>" + "c" + "</sub>"
        max_str = "<sub>" + ",max" + "</sub>"

        self.parameter_view = ParameterViewWidget("Currents & time")
        self.parameter_view.add_row("î"+a,0,"A")
        self.parameter_view.add_row("î"+a+max_str,0,"A")
        self.parameter_view.add_row("î"+b,0,"A")
        self.parameter_view.add_row("î"+b+max_str,0,"A")
        self.parameter_view.add_row("î"+c,0,"A")
        self.parameter_view.add_row("î"+c+max_str,0,"A")
        self.parameter_view.add_row("Fault time",0,"s")

        sub_d = "<sub>" + "d" + "</sub>"
        sub_line = "<sub>" + "k" + "</sub>"

        self.x_parameter_view = ParameterViewWidget("Reactances")
        self.x_parameter_view.add_row("X"+sub_d+"''",0.914,"Ω")
        self.x_parameter_view.add_row("X"+sub_d+"'",1.767,"Ω")
        self.x_parameter_view.add_row("X"+sub_d,9.552,"Ω")
        self.x_parameter_view.add_row("R"+sub_d,0.0052,"Ω")
        self.x_parameter_view.add_row("X"+sub_line,1.0,"Ω")
        self.x_parameter_view.add_row("R"+sub_line,1.0,"Ω")

        self.image = PictureViewWidget("short_circuit.png")

        def fault_button_clicked():
            setattr(simulator,"fault",True)
            self.fault_button.setDisabled(True)

        self.fault_button = QPushButton(self)
        self.fault_button.setText("Create 3-phase short circuit")
        self.fault_button.setCheckable(True)
        self.fault_button.clicked.connect(fault_button_clicked)

        k = "<sub>" + "k" + "</sub>"
        self.slider_value = QLabel(self)
        self.slider_value.setText("Short circuit power (S"+k+")= " +
                            str(getattr(simulator,"short_circuit_power")) + " MVA")

        self.power_slider = QSlider(Qt.Horizontal)
        self.power_slider.setMaximum(5*10**3)
        self.power_slider.setMinimum(20)
        self.power_slider.setValue(getattr(simulator,"short_circuit_power"))
        self.power_slider.valueChanged.connect(
            lambda: s_power_changed(self.power_slider.value()))

        def s_power_changed(inp):
            self.slider_value.setText("Short circuit power (S"+k+")= " + str(inp) + ".0 MVA")
            setattr(simulator,"short_circuit_power",inp)


        self.simulation_view_layout.addWidget(self.image,0,0,1,2)
        self.simulation_view_layout.addWidget(self.parameter_view,0,2,1,1)
        self.simulation_view_layout.addWidget(self.x_parameter_view,0,3,1,1)
        self.simulation_view_layout.addWidget(self.fault_button,1,0,1,4)
        self.simulation_view_layout.addWidget(self.power_slider,2,0,1,3)
        self.simulation_view_layout.addWidget(self.slider_value,2,3,1,1)
        self.current_graph.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.simulation_view_layout.addWidget(self.current_graph,3,0,1,4)


        self.setLayout(self.simulation_view_layout)



    @Slot(list)
    def update(self, inp):
        '''update Slot method is run once every graphing interval.
           Should contain updates of all visual elements.
           Data from simulator is contained in input variable with default name "inp".
           inp is a type=list and the data is in the same order it is send from the simulator
           as "send_to_graph function call.
           last line of the method must be call for self.graphing_flow_control()'''

        self.current_graph.step("Ia",inp[0][0])
        self.current_graph.step("Ib",inp[0][1])
        self.current_graph.step("Ic",inp[0][2])

        self.parameter_view.update_row(0,inp[2][0])
        self.parameter_view.update_row(1,inp[1][0])
        self.parameter_view.update_row(2,inp[2][1])
        self.parameter_view.update_row(3,inp[1][1])
        self.parameter_view.update_row(4,inp[2][2])
        self.parameter_view.update_row(5,inp[1][2])
        if inp[3] > 0:
            self.parameter_view.update_row(6,inp[3])

        if inp[5] >= 0:
            if inp[6]:
                self.current_graph.steptime = inp[7]
                self.x_parameter_view.update_row(0,inp[9][0])
                self.x_parameter_view.update_row(1,inp[9][1])
                self.x_parameter_view.update_row(2,inp[9][2])
                self.x_parameter_view.update_row(3,inp[9][3])
                self.x_parameter_view.update_row(4,inp[9][4])
                self.x_parameter_view.update_row(5,inp[9][5])
            if inp[8]:
                self.current_graph.steptime = inp[7]



        ### LAST LINE OF UPDATE METHOD, DO NOT EDIT OR ADD CODE AFTER
        self.graphing_flow_control()
        ### LAST LINE OF UPDATE METHOD, DO NOT EDIT OR ADD CODE AFTER
