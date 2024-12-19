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
from numpy.linalg import inv
parent_directory = os.path.abspath('../Z_DI_Simulator')
sys.path.append('..')
from LinePlotWidget import LinePlotWidget
from SimulationWindowWidgets import PictureViewWidget



class parameters():
    '''parameters object is used to declare and contain simualtion parameters and
       input vaiables.
       Required parameters: simulation_name, steptime, simulation_time, graphing_interval
       The input variables are declared in input_parameters dictionary.'''
    def __init__(self):

        self.simulation_name = "Frequency converter simulation"
        self.steptime = 0.000005
        self.simulation_time = 0
        self.data_length = 500000
        self.graphing_interval = 10     # graphs are only redrawn every xth step to reduce load


        self.input_parameters = {
            "u_in":{
                "display_name": "Input voltage",
                "symbol": "U_i_n",
                "editable": True,
                "type": "number",
                "init_value": 230,
                "unit": "V",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1000,
                "minimum": 0
            },
            "f_fund":{
                "display_name": "Fundamental frequency",
                "symbol": "f_n",
                "editable": True,
                "type": "number",
                "init_value": 50,
                "unit": "Hz",
                "default_prefix": 0,
                "prefix_limits": [0,3],
                "maximum":100,
                "minimum": 25
            },
            "f_sw":{
                "display_name": "Switching frequency",
                "symbol": "f_s_w",
                "editable": True,
                "type": "number",
                "init_value":1000,
                "unit": "Hz",
                "default_prefix": 0,
                "prefix_limits": [0,3],
                "maximum":5000,
                "minimum": 0
            },
            "mod_ind":{
                "display_name": "Modulation index",
                "symbol": "k",
                "editable": True,
                "type": "number",
                "init_value":1,
                "unit": "",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum": 1,
                "minimum": 0.1
            },
            "load_resistance":{
                "display_name": "Load resistance",
                "symbol": "R_l_o_a_d",
                "editable": False,
                "type": "number",
                "init_value": 10,
                "unit": "Ω",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum":1000,
                "minimum": 1
            },
            "load_inductance":{
                "display_name": "Load inductance",
                "symbol": "L_l_o_a_d",
                "editable": False,
                "type": "number",
                "init_value": 0.20,
                "unit": "H",
                "default_prefix": 0,
                "prefix_limits": [-6,0],
                "maximum":1,
                "minimum": 1*10**-5
            },
            "load_capacitance":{
                "display_name": "Load capacitance",
                "symbol": "C_l_o_a_d",
                "editable": False,
                "type": "number",
                "init_value": 0.00001,
                "unit": "F",
                "default_prefix": 0,
                "prefix_limits": [-6,0],
                "maximum": 1,
                "minimum": 1*10**-6
            },
            "filter_resistance":{
                "display_name": "Filter resistance",
                "symbol": "R_f_i_l_t_e_r",
                "editable": False,
                "type": "number",
                "init_value": 0.001,
                "unit": "Ω",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum":1000,
                "minimum": 1*10**-4
            },
            "filter_inductance":{
                "display_name": "Filter inductance",
                "symbol": "L_f_i_l_t_e_r",
                "editable": False,
                "type": "number",
                "init_value": 0.01,
                "unit": "H",
                "default_prefix": 0,
                "prefix_limits": [-6,0],
                "maximum":1,
                "minimum": 1*10**-5
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

        self.steps = 0
        self.update_static_graphs = True
        self.update_static_graphs_wait = 0


        self.input_variables = np.array(
            [self.params.input_parameters["u_in"]["init_value"],#0
             self.params.input_parameters["f_fund"]["init_value"],#1
             self.params.input_parameters["f_sw"]["init_value"],#2
             self.params.input_parameters["mod_ind"]["init_value"],#3
             self.params.input_parameters["load_resistance"]["init_value"],#4
             self.params.input_parameters["load_inductance"]["init_value"],#5
             self.params.input_parameters["load_capacitance"]["init_value"],#6
             self.params.input_parameters["filter_resistance"]["init_value"],
             self.params.input_parameters["filter_inductance"]["init_value"]
             ], dtype=float
        )

        i = 0
        for _, var in enumerate(self.params.input_parameters.keys()):
            if self.params.input_parameters[var]["type"] == "number":
                self.input_variables[i] *= 10**self.params.input_parameters[var]["default_prefix"]
                i += 1

        self.input_texts = [

        ]

        self.state_vector = np.array([[0.0, 0.0],
                                      [0.0, 0.0],
                                      [0.0, 0.0]])

        self.voltages = np.array([0,0,0],dtype=float)
        self.I_prev = np.array([0,0,0],dtype=float)
        self.delta_i = np.array([0,0,0],dtype=float)
        self.V_L_load = np.array([0,0,0],dtype=float)


        self.old_frequency = 0
        self.frequency_change_called = False
        self.frequency_change_enabled = False
        self.new_step_num = 0

        self.update_matrixes()



    def update_matrixes(self):
        '''Function is executed after updating inputs either by user clicking the update button,
           or by changing input varibles when autoupdate is on. 
           Additionally fun at startup.
           This fuction should include all calculations not necessary to run every cycle but after 
           user action.'''
        self.update_static_graphs = True
        self.update_static_graphs_wait = 0
        sine_len = 1/self.input_variables[1]
        self.step_num = round(sine_len/self.params.steptime)
        # modulation sine wave array
        self.sine_array = np.array([np.zeros((self.step_num,),dtype=float),
                                    np.zeros((self.step_num,),dtype=float),
                                    np.zeros((self.step_num,),dtype=float)])
        # modulation triangle wave array
        self.tri_array = np.zeros((self.step_num,),dtype=float)
        # pwm modulation array
        self.pwm_array = np.array([np.zeros((self.step_num,),dtype=float),
                                   np.zeros((self.step_num,),dtype=float),
                                   np.zeros((self.step_num,),dtype=float)])
        # pwm switching point array
        self.pwm_sw_array = np.array([np.zeros((self.step_num,),dtype=float),
                                      np.zeros((self.step_num,),dtype=float),
                                      np.zeros((self.step_num,),dtype=float)])
        # time array
        self.x_time = np.linspace(0,sine_len,self.step_num)
        # sine wave y-value over time over one wave period
        self.x_sine = np.linspace(0,(2*np.pi),self.step_num)

        tri_len = 1/(self.input_variables[2]/2)
        tri_num = sine_len/tri_len

        tri_y_step = 2/(self.step_num/tri_num)*2

        tri_dir = 2
        angle_2 = (4*np.pi)/3
        angle_3 = (2*np.pi)/3
        # loops over time array and computes the vaules of other previous arrays over the given time
        for i,_ in enumerate(self.x_time):
            self.sine_array[0][i] = np.sin(self.x_sine[i])*self.input_variables[3]
            self.sine_array[1][i] = np.sin(self.x_sine[i]-angle_2)*self.input_variables[3]
            self.sine_array[2][i] = np.sin(self.x_sine[i]-angle_3)*self.input_variables[3]
            self.tri_array[i] = self.tri_array[i-1]+(tri_dir*tri_y_step)
            if self.tri_array[i] >= 1:
                tri_dir = -1*tri_dir
            elif self.tri_array[i] <= -1:
                tri_dir = -1*tri_dir
            # Loop over the phases
            for j in range(0,3):
                if self.tri_array[i] >= self.sine_array[j][i]:
                    self.pwm_array[j][i] = -1
                else:
                    self.pwm_array[j][i] = 1
                if i == 0:
                    self.pwm_sw_array[j][i] = 1
                    continue
                if self.pwm_array[j][i] == self.pwm_array[j][i-1]:
                    self.pwm_sw_array[j][i] = 1
                else:
                    self.pwm_sw_array[j][i] = 0

        # time_len is lenght of time vector
        self.time_len = len(self.pwm_array[0])#/graph_var
        self.time_len_i = self.time_len-1

        # load and filter parameters
        self.R_load = self.input_variables[4]
        self.R_filter = self.input_variables[7]
        self.L_load = self.input_variables[5]
        self.L_filter = self.input_variables[8]
        self.C_load = self.input_variables[6]
        self.R = self.R_load+self.R_filter
        self.L = self.L_load+self.R_filter
        self.C = self.C_load

        # L and R ratio are used to compute voltages
        self.L_ratio = self.L/self.L_filter
        self.R_ratio = self.R/self.R_filter

        # system matrix
        A00 = self.L*self.C
        A01 = 0
        A10 = 0
        A11 = 1

        self.A_matrix = np.array([[A00,A01],
                                  [A10,A11]], dtype=float)
        # inversion of system matrix
        self.A_INV = inv(self.A_matrix)

        # output matrix
        B00 = self.R*self.C
        B01 = 1
        B10 = -1
        B11 = 0
        self.B_matrix = np.array([[B00,B01],
                                  [B10,B11]], dtype=float)

        self.U_in = self.input_variables[0]/2

        # input vector
        self.input_vect = np.array([self.U_in,0], dtype=float)



    @Slot(bool)
    def run(self, _):
        '''Simulation calculation method. 
        This method shoud include simulation step calculation and method for sending data to graph.
        Calculation loop is run as long as simulation is set ON by user.
        Data is sent to the graph via self.send_to_graph() function which should be called at the
        end of the method. This fucntion takes 1 input type=list, which should contain all data to
        be send for graphs or other visual elements in graphicsViewWidget'''
        while self.flow_control():
            if self.update_static_graphs:
                self.steps = 0
            # loops over all three phases and computes the state vector using trapezoidal
            # approximation
            for phase in range(0,3):
                self.state_vector[phase] = (self.state_vector[phase]+
                                            self.trapz_step(self.state_vector[phase],
                                            self.params.steptime, phase))

            # computes the system currents from the state values and capacitances for all phases
            currents = [self.state_vector[0][0]*self.C,
                        self.state_vector[1][0]*self.C,
                        self.state_vector[2][0]*self.C]

            for phase in range(0,3):
                # delta_i is the current difference between steps
                self.delta_i[phase] = currents[phase]-self.I_prev[phase]
                # I_prev is current vector of previous step, used to compute delta_i and rewritten after it
                self.I_prev[phase] = currents[phase]
                # V_L_load is the voltage over load inductance U=L*(di/dt)
                self.V_L_load[phase] = (self.L/self.L_ratio)*(self.delta_i[phase]/self.params.steptime)
                # voltages is load voltage vector, sum of load inductor capacitor and resistor voltages
                self.voltages[phase] = self.V_L_load[phase]+self.state_vector[phase][1]+(currents[phase]*self.R/self.R_ratio)


            # sends data to graphs
            self.send_to_graph([[self.x_time,self.sine_array,self.tri_array],#0
                                [self.x_time, self.pwm_array],#1
                                currents[0],#2
                                currents[1],#3
                                currents[2],#4
                                self.x_time[self.steps],#5
                                self.update_static_graphs,#6
                                self.voltages
                                ])

            # handles the updates of the modulation graphs. Only updated when input is changed
            # to reduce computational load
            self.steps += 1
            if self.steps >= self.time_len_i:
                self.steps = -1
            if self.update_static_graphs:
                self.update_static_graphs_wait += 1
                if self.update_static_graphs_wait > self.params.graphing_interval:
                    self.update_static_graphs = False



    def compute_input(self, t_fi, phase):
        '''computes the input at given sub-timestep'''
        self.input_vect[0] = self.pwm_array[phase][self.steps]*self.U_in*t_fi
        return self.input_vect


    def trapz_step(self, y_tz, dt, phase):
        '''computes step using trapezoidal approximation'''
        # voltage and change calculation for the timestep n
        u_t = self.compute_input(self.pwm_sw_array[phase][self.steps], phase)
        y0 = (self.A_INV.dot(u_t - self.B_matrix.dot(y_tz)))
        # voltage and change calculation for the timestep n+1
        u_t = self.compute_input(self.pwm_sw_array[phase][self.steps+1], phase)
        y1 = (self.A_INV.dot(u_t - self.B_matrix.dot(y_tz)))
        dy = dt/2*(y1+y0)
        return dy



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
        screen_width = parent.screen_geometry.width()
        parent.parameter_view_size = 210

        space_for_param_edit = 330
        self.modulation_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                        plot_step=self.parameters.graphing_interval,
                                        x_lenght=1000, enable_legend=True,
                                        x_name="wave period [s]", y_name="y")
        self.modulation_graph.add_plotline("Phase a",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.modulation_graph.add_plotline("Phase b",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.modulation_graph.add_plotline("Phase c",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="blue")
        self.modulation_graph.add_plotline("Carrier",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="orange")
        self.modulation_graph.add_plotline("time",x_data=np.array([0,0,0]),
                                    y_data=np.array([-1,0,1]),color="magenta")
        self.modulation_graph.set_text(title="Modulation")
        self.modulation_graph.change_line_pen("time",linetype="..", width=2)
        self.modulation_graph.setMaximumWidth((screen_width-space_for_param_edit)*0.4)


        self.pwm_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                        plot_step=self.parameters.graphing_interval,
                                        x_lenght=1000, enable_legend=True,
                                        x_name="wave period [s]", y_name="y")
        self.pwm_graph.add_plotline("Phase a",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.pwm_graph.add_plotline("Phase b",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.pwm_graph.add_plotline("Phase c",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="blue")
        self.pwm_graph.set_text(title="PWM signal")
        self.pwm_graph.setMaximumWidth((screen_width-space_for_param_edit)*0.4)


        self.output_I_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                        plot_step=self.parameters.graphing_interval,
                                        x_lenght=5000, enable_legend=True,
                                        x_name="time [s]", y_name="load current [A]")
        self.output_I_graph.add_plotline("Phase a",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.output_I_graph.add_plotline("Phase b",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.output_I_graph.add_plotline("Phase c",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="blue")
        self.output_I_graph.set_text(title="Output currents")
        self.output_I_graph.setMaximumWidth((screen_width-space_for_param_edit)*0.6)


        self.output_U_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                        plot_step=self.parameters.graphing_interval,
                                        x_lenght=5000, enable_legend=True,
                                        x_name="time [s]", y_name="Load voltage [V]")
        self.output_U_graph.add_plotline("Phase a",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.output_U_graph.add_plotline("Phase b",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.output_U_graph.add_plotline("Phase c",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="blue")
        self.output_U_graph.set_text(title="Output voltages")
        self.output_U_graph.setMaximumWidth((screen_width-space_for_param_edit)*0.6)

        self.figure = PictureViewWidget("frequency_converter.png")

        self.simulation_view_layout.addWidget(self.output_U_graph,0,0,3,1)
        self.simulation_view_layout.addWidget(self.output_I_graph,3,0,3,1)
        self.simulation_view_layout.addWidget(self.figure,0,1,2,1)
        self.simulation_view_layout.addWidget(self.modulation_graph,2,1,2,1)
        self.simulation_view_layout.addWidget(self.pwm_graph,4,1,2,1)

        self.setLayout(self.simulation_view_layout)



    @Slot(list)
    def update(self, inp):
        '''update Slot method is run once every graphing interval.
           Should contain updates of all visual elements.
           Data from simulator is contained in input variable with default name "inp".
           inp is a type=list and the data is in the same order it is send from the simulator
           as "send_to_graph function call.
           last line of the method must be call for self.graphing_flow_control()'''

        # only updated when inputs are updated
        if inp[6]:
            self.modulation_graph.update("Phase a",inp[0][0],inp[0][1][0])
            self.modulation_graph.update("Phase b",inp[0][0],inp[0][1][1])
            self.modulation_graph.update("Phase c",inp[0][0],inp[0][1][2])
            self.modulation_graph.update("Carrier",inp[0][0],inp[0][2])

            self.pwm_graph.update("Phase a",inp[1][0],inp[1][1][0])
            self.pwm_graph.update("Phase b",inp[1][0],inp[1][1][1])
            self.pwm_graph.update("Phase c",inp[1][0],inp[1][1][2])

        self.modulation_graph.update("time",x_data_new=[inp[5],inp[5]],y_data_new=[-1,1])

        self.output_I_graph.step("Phase a",inp[2])
        self.output_I_graph.step("Phase b",inp[3])
        self.output_I_graph.step("Phase c",inp[4])

        self.output_U_graph.step("Phase a",inp[7][0])
        self.output_U_graph.step("Phase b",inp[7][1])
        self.output_U_graph.step("Phase c",inp[7][2])

        ### LAST LINE OF UPDATE METHOD
        self.graphing_flow_control()
        ### LAST LINE OF UPDATE METHOD
