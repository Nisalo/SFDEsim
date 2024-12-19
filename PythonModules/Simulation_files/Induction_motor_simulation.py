
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
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import (QGridLayout, QWidget)
import numpy as np
parent_directory = os.path.abspath('../Z_DI_Simulator')
sys.path.append('..')
from LinePlotWidget import LinePlotWidget


# motor type 3GBA 112 410-ADDIN

class parameters():
    '''parameters object is used to declare and contain simualtion parameters and
       input vaiables.
       Required parameters: simulation_name, steptime, simulation_time, graphing_interval
       The input variables are declared in input_parameters dictionary.'''
    def __init__(self):

        self.simulation_name = "Induction motor simulation"
        self.steptime = 0.01
        self.simulation_time = 0
        self.data_length = 500000
        self.graphing_interval = 20     # graphs are only redrawn every xth step to reduce load


        self.input_parameters = {
            "target_rpm":{
                "display_name": "Target RPM",
                "symbol": "n_t_a_r_g_e_t",
                "editable": True,
                "type": "number",
                "init_value": 0,
                "unit": "rpm",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1500,
                "minimum":0
            },
            "acceleration":{
                "display_name": "Acceleration",
                "symbol": "α",
                "editable": True,
                "type": "number",
                "init_value": 250,
                "unit": "rpm/s",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1000,
                "minimum":0
            },
            "load_torque":{
                "display_name": "Load torque",
                "symbol": "T_l_o_a_d",
                "editable": True,
                "type": "number",
                "init_value": 0.4,
                "unit": "Nm",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1000,
                "minimum":0
            },
            "motor_moment_of_inertia":{
                "display_name": "Motor moment of inertia",
                "symbol": "J_m",
                "editable": True,
                "type": "number",
                "init_value": 0.02,
                "unit": "kgm^2",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":10,
                "minimum":0
            },
            "load_moment_of_inertia":{
                "display_name": "Load moment of inertia",
                "symbol": "J_l_o_a_d",
                "editable": True,
                "type": "number",
                "init_value": 1,
                "unit": "kgm^2",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":50,
                "minimum":0
            },
            "load_time":{
                "display_name": "Load connection time",
                "symbol": "t_l_o_a_d",
                "editable": True,
                "type": "number",
                "init_value": 1000,
                "unit": "ms",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":10000,
                "minimum":0
            },
            "nominal_torque":{
                "display_name": "Nominal torque",
                "symbol": "T_n",
                "editable": False,
                "type": "number",
                "init_value": 24.4,
                "unit": "Nm",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1000,
                "minimum":0
            },
            "maximum_torque":{
                "display_name": "Maximum torque",
                "symbol": "T_m_a_x",
                "editable": False,
                "type": "number",
                "init_value": 390,
                "unit": "%",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1000,
                "minimum":0
            },
            "nominal_power":{
                "display_name": "Nominal power",
                "symbol": "P_n",
                "editable": False,
                "type": "number",
                "init_value": 3.9,
                "unit": "kW",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1000,
                "minimum":0
            },
            "nominal_current":{
                "display_name": "Nominal current",
                "symbol": "I_n",
                "editable": False,
                "type": "number",
                "init_value": 7.7,
                "unit": "A",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1000,
                "minimum":0
            },
            "motor_cos_phi":{
                "display_name": "Motor cos(φ)",
                "symbol": "",
                "editable": False,
                "type": "number",
                "init_value": 0.76,
                "unit": "",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1,
                "minimum":0
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
            [self.params.input_parameters["target_rpm"]["init_value"],#0
             self.params.input_parameters["acceleration"]["init_value"],#1
             self.params.input_parameters["load_torque"]["init_value"],#2
             self.params.input_parameters["motor_moment_of_inertia"]["init_value"],#3,
             self.params.input_parameters["motor_cos_phi"]["init_value"],#4
             self.params.input_parameters["load_time"]["init_value"],#5
             self.params.input_parameters["nominal_torque"]["init_value"],#6
             self.params.input_parameters["maximum_torque"]["init_value"],#7
             self.params.input_parameters["nominal_power"]["init_value"],#8
             self.params.input_parameters["nominal_current"]["init_value"],#9
             self.params.input_parameters["motor_cos_phi"]["init_value"]
             ], dtype=float
        )

        i = 0
        for _, var in enumerate(self.params.input_parameters.keys()):
            if self.params.input_parameters[var]["type"] == "number":
                self.input_variables[i] *= 10**self.params.input_parameters[var]["default_prefix"]
                i += 1

        self.input_texts = [

        ]

        self.pi2 = 2*np.pi
        self.current_rpm = 0
        self.load_J_memo = [0,0]
        self.J_changed = 100*10**3
        self.J_tot = 0
        self.T_dyn_acc = 0
        self.T_dyn_J = 0
        self.P_out = 0
        self.current_acceleration = 0

        self.phase_angles = np.array([0,
                                -2*np.pi/3,
                                -4*np.pi/3],
                                dtype=float)

        self.update_matrixes()



    def update_matrixes(self):
        '''Function is executed after updating inputs either by user clicking the update button,
           or by changing input varibles when autoupdate is on. 
           Additionally fun at startup.
           This fuction should include all calculations not necessary to run every cycle but after 
           user action.'''
        self.target_rpm = self.input_variables[0]
        self.acceleration = self.input_variables[1]
        self.T_load = self.input_variables[2]
        self.J_m = self.input_variables[3]
        self.J_load = self.input_variables[4]
        self.J_time = self.input_variables[5]*0.001
        self.T_nom = self.input_variables[6]
        self.T_max_percent = self.input_variables[7]
        self.P_nom = self.input_variables[8]
        self.I_nom = self.input_variables[9]
        self.cos_phi = self.input_variables[10]

        # If inertia is 0, it will cause divide by zero error, this solves the problem
        if self.J_m <= 0:
            self.J_m = 1*10**-15


        self.sin_phi = np.sin(np.arccos(self.cos_phi))
        self.T_max = self.T_nom*(self.T_max_percent*0.01)

        # T_dir is the direction of acceleration and torque, if rpm increases T_dir is positive
        # if rpm is decreasing T_dir is negative
        if self.target_rpm > self.current_rpm:
            self.T_dir = 1
        elif self.target_rpm < self.current_rpm:
            self.T_dir = -1
        else:
            self.T_dir = 0

        self.load_J_memo[1] = self.load_J_memo[0]
        self.load_J_memo[0] = self.J_load
        self.J_load_change = self.load_J_memo[0]-self.load_J_memo[1]
        if self.J_load_change > 0:
            self.J_changed = 0
            self.T_dir = 1
        elif self.J_load_change < 0:
            self.J_changed = 0
            self.T_dir = -1


    @Slot(bool)
    def run(self, _):
        '''Simulation calculation method. 
        This method shoud include simulation step calculation and method for sending data to graph.
        Calculation loop is run as long as simulation is set ON by user.
        Data is sent to the graph via self.send_to_graph() function which should be called at the
        end of the method. This fucntion takes 1 input type=list, which should contain all data to
        be send for graphs or other visual elements in graphicsViewWidget'''
        while self.flow_control():

            self.J_tot = self.J_m+self.J_load
            # dynamic torque due acceleration
            self.T_dyn_acc = self.get_dynamic_torque()
            # dynamic torque due load change
            self.T_dyn_J = self.get_dynamic_torque_J()

            # total torque
            T = self.T_dyn_acc+self.T_load+self.T_dyn_J

            # RPM decrease caused by loading exceeding maximum torque
            rpm_dec_step = 0
            if T > self.T_max:
                T_d = self.T_max-T
                rpm_dec_step = ((T_d)/(self.J_tot))*self.params.steptime

            # change of rpm over the simulation timestep
            rpm_step = ((self.T_dyn_acc)/(self.J_tot))*self.params.steptime

            # current rpm
            self.current_rpm = round(self.current_rpm + rpm_step + rpm_dec_step,4)

            # output power of motor
            self.P_out = ((T-self.T_dyn_J)*self.current_rpm)/9550

            self.current_acceleration = self.acceleration*self.T_dir

            # motor reactive current
            I_sd = self.I_nom*(self.sin_phi+self.cos_phi*(np.sqrt((self.T_max/self.T_nom)**2-1)-
                                                          np.sqrt((self.T_max/self.T_nom)**2-
                                                                  (T/self.T_nom)**2)))

            # motor active current
            I_sq = self.I_nom*(T/self.T_nom)*self.cos_phi

            # total motor current
            I = np.sqrt(I_sd**2+I_sq**2)



            # data sent to graphs
            self.send_to_graph([self.current_rpm,#0
                                [T,self.T_load, self.T_dyn_acc],#1
                                [self.P_out],#2
                                [I],#3
                                self.target_rpm])#4


    def get_dynamic_torque_J(self):
        '''Calculates dynmaic torque when load momonet of inertia is changed'''
        T = 0
        if self.J_changed < self.J_time/self.params.steptime:
            self.J_changed += 1
            T = self.current_rpm*(self.pi2/60)*(self.J_load_change/self.J_time)
        return T


    def get_dynamic_torque(self):
        '''calculates the dynamic torque'''
        T = 0
        if self.T_dir > 0:          # if motor has positive acceleration
            if self.current_rpm < self.target_rpm:
                T = self.J_tot*(self.pi2/60)*(self.acceleration)*self.T_dir
        elif self.T_dir < 0:        # if motor has negative acceleration
            if self.current_rpm > self.target_rpm:
                T = self.J_tot*(self.pi2/60)*(self.acceleration)*self.T_dir
        else:
            return T # if no acceleration -> dynamic torque = 0
        # if the sum load torque and dynamic torque are more than the maximum torque of motor,
        # the dynamic torque is limited to maximum torque of the motor
        if abs(T)+self.T_load > self.T_max:
            T = (self.T_max-self.T_load)*self.T_dir
        return T





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
        parent.parameter_view_size = 200
        pen_widht = 2
        x_len = 1500

        self.rpm_graph = LinePlotWidget(simu_steptime=self.parameters.steptime/10,
                                              plot_step=self.parameters.graphing_interval,
                                              x_lenght=x_len, enable_legend=True,
                                              x_name="time [s]", y_name="n [rpm]")
        self.rpm_graph.add_plotline("motor speed",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.rpm_graph.add_plotline("target speed",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.rpm_graph.set_text(title="Motor speed")
        self.rpm_graph.change_line_pen("motor speed",width=pen_widht)
        self.rpm_graph.change_line_pen("target speed",width=pen_widht, linetype="..")


        self.torque_graph = LinePlotWidget(simu_steptime=self.parameters.steptime/10,
                                              plot_step=self.parameters.graphing_interval,
                                              x_lenght=x_len, enable_legend=True,
                                              x_name="time [s]", y_name="Torque [Nm]")
        self.torque_graph.add_plotline("T_total",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.torque_graph.add_plotline("T_load",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="magenta")
        self.torque_graph.add_plotline("T_acceleration",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="cyan")
        self.torque_graph.set_text(title="Torque")
        self.torque_graph.change_line_pen("T_total",width=pen_widht)
        self.torque_graph.change_line_pen("T_load",width=pen_widht)
        self.torque_graph.change_line_pen("T_acceleration",width=pen_widht)


        self.power_graph = LinePlotWidget(simu_steptime=self.parameters.steptime/10,
                                              plot_step=self.parameters.graphing_interval,
                                              x_lenght=x_len, enable_legend=True,
                                              x_name="time [s]", y_name="Power [kW]")
        self.power_graph.add_plotline("P_out",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.power_graph.set_text(title="Motor power")
        self.power_graph.change_line_pen("P_out",width=pen_widht)


        self.current_graph = LinePlotWidget(simu_steptime=self.parameters.steptime/10,
                                              plot_step=self.parameters.graphing_interval,
                                              x_lenght=x_len, enable_legend=True,
                                              x_name="time [s]", y_name="current [A]")
        self.current_graph.add_plotline("I",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.current_graph.set_text(title="Motor current")
        self.current_graph.change_line_pen("I",width=pen_widht)


        self.simulation_view_layout.addWidget(self.rpm_graph,0,0,1,1)
        self.simulation_view_layout.addWidget(self.torque_graph,1,0,1,1)
        self.simulation_view_layout.addWidget(self.power_graph,0,1,1,1)
        self.simulation_view_layout.addWidget(self.current_graph,1,1,1,1)

        self.setLayout(self.simulation_view_layout)



    @Slot(list)
    def update(self, inp):
        '''update Slot method is run once every graphing interval.
           Should contain updates of all visual elements.
           Data from simulator is contained in input variable with default name "inp".
           inp is a type=list and the data is in the same order it is send from the simulator
           as "send_to_graph function call.
           last line of the method must be call for self.graphing_flow_control()'''

        self.rpm_graph.step("motor speed",inp[0])
        self.rpm_graph.step("target speed",inp[4])

        self.torque_graph.step("T_total",inp[1][0])
        self.torque_graph.step("T_load",inp[1][1])
        self.torque_graph.step("T_acceleration",inp[1][2])

        self.power_graph.step("P_out",inp[2][0])

        self.current_graph.step("I",inp[3][0])

        ### LAST LINE OF UPDATE METHOD
        self.graphing_flow_control()
        ### LAST LINE OF UPDATE METHOD
