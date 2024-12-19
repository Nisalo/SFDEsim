
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
from PySide6.QtWidgets import (QGridLayout, QWidget, QComboBox)
import numpy as np
from numpy.linalg import inv
parent_directory = os.path.abspath('../Z_DI_Simulator')
sys.path.append('..')
from LinePlotWidget import LinePlotWidget



class parameters():
    '''parameters object is used to declare and contain simualtion parameters and
       input vaiables.
       Required parameters: simulation_name, steptime, simulation_time, graphing_interval
       The input variables are declared in input_parameters dictionary.'''
    def __init__(self):

        self.simulation_name = "Spring-Mass-Damper simulation"
        self.steptime = 0.001
        self.simulation_time = 0
        self.data_length = 50000
        self.graphing_interval = 25     # graphs are only redrawn every xth step to reduce load


        self.input_parameters = {
            "force_amp":{
                "display_name": "Force amplitude",
                "symbol": "F",
                "editable": True,
                "type": "number",
                "init_value": 1,
                "unit": "N",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1000,
                "minimum": 0
            },
            "force_type":{
                "display_name": "Force type",
                "symbol": "",
                "editable": True,
                "type": "dropdown",
                "items": ["Sinusoidal", "Static"],
                "unit": ""
            },
            "steptime":{
                "display_name": "Steptime",
                "symbol": "t_s_t_e_p",
                "editable": True,
                "type": "number",
                "init_value": 0.001,
                "unit": "s",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":10,
                "minimum": 0
            },
            "mass":{
                "display_name": "Mass",
                "symbol": "m",
                "editable": False,
                "type": "number",
                "init_value": 2,
                "unit": "kg",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":10,
                "minimum": 0
            },
            "spring_constant":{
                "display_name": "Spring constant",
                "symbol": "k",
                "editable": False,
                "type": "number",
                "init_value": 2,
                "unit": "",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":10,
                "minimum": 10**-1
            },
            "damping_factor":{
                "display_name": "Damping factor",
                "symbol": "ζ",
                "editable": False,
                "type": "number",
                "init_value": 1,
                "unit": "Ns/m",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":10,
                "minimum": 0
            },
            "omega":{
                "display_name": "Force angular frequency",
                "symbol": "ω_F",
                "editable": False,
                "type": "number",
                "init_value": 1,
                "unit": "Hz",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":100,
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
    shown_graphs = 1
    def __init__(self, parent, params, signals, send_to_graph):
        super().__init__()

        print("initilzing simulator: Reference frame simulation")
        ### Do not change ###
        self.params = params
        self.signals = signals
        self.F_rklow_control = parent.simulation_flow_control
        self.send_to_graph = send_to_graph
        ### Do not change ###


        self.input_variables = np.array(
            [self.params.input_parameters["force_amp"]["init_value"],#0
             self.params.input_parameters["steptime"]["init_value"],#1
             self.params.input_parameters["mass"]["init_value"],#2
             self.params.input_parameters["spring_constant"]["init_value"],#3
             self.params.input_parameters["damping_factor"]["init_value"],
             self.params.input_parameters["omega"]["init_value"]
             ], dtype=float
        )

        i = 0
        for _, var in enumerate(self.params.input_parameters.keys()):
            if self.params.input_parameters[var]["type"] == "number":
                self.input_variables[i] *= 10**self.params.input_parameters[var]["default_prefix"]
                i += 1

        self.input_texts = [
             self.params.input_parameters["force_type"]["items"][0]
        ]

        self.y_vect_rk = np.array([0,0])
        self.y_vect_tz = np.array([0,0])
        self.y_vect_fe = np.array([0,0])
        self.step_time_mem = [0,0]
        self.steptime_changed = False

        self.update_matrixes()



    def update_matrixes(self):
        '''Function is executed after updating inputs either by user clicking the update button,
           or by changing input varibles when autoupdate is on. 
           Additionally fun at startup.
           This fuction should include all calculations not necessary to run every cycle but after 
           user action.'''
        self.omega = self.input_variables[5]        # Force fuction angular frequency 1.0

        self.A_matrix = np.array([[self.input_variables[2],0],  #mass
                                  [0,1]], dtype=float)

        self.B_matrix = np.array([[self.input_variables[4],     #spring
                                   self.input_variables[3]],    #damping
                                   [-1,0]], dtype=float)

        self.F_amp = self.input_variables[0]

        self.F_rk = np.array([0.0,0.0], dtype=float)
        self.F_tz = np.array([0.0,0.0], dtype=float)
        self.F_fe = np.array([0.0,0.0], dtype=float)

        self.A_INV = inv(self.A_matrix)

        self.params.steptime = self.input_variables[1]

        self.step_time_mem[1] = self.step_time_mem[0]
        self.step_time_mem[0] = self.input_variables[1]
        if self.step_time_mem[1] != self.step_time_mem[0]:
            self.steptime_changed = True



    @Slot(bool)
    def run(self, _):
        '''Simulation calculation method. 
        This method shoud include simulation step calculation and method for sending data to graph.
        Calculation loop is run as long as simulation is set ON by user.
        Data is sent to the graph via self.send_to_graph() function which should be called at the
        end of the method. This fucntion takes 1 input type=list, which should contain all data to
        be send for graphs or other visual elements in graphicsViewWidget'''
        while self.F_rklow_control():

            self.y_vect_rk = self.y_vect_rk + self.RK4_step(self.y_vect_rk,
                                                      self.params.simulation_time,
                                                      self.params.steptime)

            if getattr(simulator,"shown_graphs"):
                self.y_vect_tz = self.y_vect_tz + self.trapz_step(self.y_vect_tz,
                                                        self.params.simulation_time,
                                                        self.params.steptime)

                self.y_vect_fe = self.y_vect_fe + self.forward_euler_step(self.y_vect_fe,
                                                        self.params.simulation_time,
                                                        self.params.steptime)

            self.send_to_graph([[self.y_vect_rk,self.F_rk],
                                [self.y_vect_tz,self.F_tz],
                                [self.y_vect_fe,self.F_fe],
                                [self.steptime_changed,self.params.steptime],
                                getattr(simulator,"shown_graphs")])


    def compute_force_rk(self,t_fi):
        '''compute force substeps for RK4'''
        if self.input_texts[0] <= "Sinusoidal":
            self.F_rk[0] = np.sin(self.omega*t_fi)*self.F_amp
        else:
            self.F_rk[0] = self.F_amp
        f_return = self.F_rk
        return f_return


    def G(self,y_g,t_g):
        '''compute k values for RK4'''
        f_t = self.compute_force_rk(t_g)
        G_t = (self.A_INV.dot(f_t - self.B_matrix.dot(y_g)))
        return G_t


    def RK4_step(self, y_rk, t_rk ,dt):
        '''Compute RK4 step'''
        k1 = self.G(y_rk, t_rk)
        k2 = self.G(y_rk+0.5*k1*dt, t_rk+0.5*dt)
        k3 = self.G(y_rk+0.5*k2*dt, t_rk+0.5*dt)
        k4 = self.G(y_rk+k3*dt, t_rk+dt)
        dy = dt * (k1 + 2*k2 + 2*k3 + k4)/6
        return dy


    def compute_force_tz(self,t_fi):
        '''compute force substep for TZ '''
        if self.input_texts[0] <= "Sinusoidal":
            self.F_tz[0] = np.sin(self.omega*t_fi)*self.F_amp
        else:
            self.F_tz[0] = self.F_amp
        f_return = self.F_tz
        return f_return


    def trapz_step(self, y_tz, t_tz ,dt):
        '''Compute TZ step'''
        f_t = self.compute_force_tz(t_tz)
        y0 = (self.A_INV.dot(f_t - self.B_matrix.dot(y_tz)))
        f_t = self.compute_force_tz(t_tz+dt)
        y1 = (self.A_INV.dot(f_t - self.B_matrix.dot(y_tz)))
        dy = dt/2*(y1+y0)
        return dy


    def compute_force_fe(self,t_fi):
        '''compute force for FE'''
        if self.input_texts[0] <= "Sinusoidal":
            self.F_fe[0] = np.sin(self.omega*t_fi)*self.F_amp
        else:
            self.F_fe[0] = self.F_amp
        f_return = self.F_fe
        return f_return


    def forward_euler_step(self, y_fe, t_fe, dt):
        '''Compute FE step'''
        f_t = self.compute_force_fe(t_fe)
        y = dt *self.A_INV.dot(f_t - self.B_matrix.dot(y_fe))
        return y


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
        parent.parameter_view_size = 190

        self.rk_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                              plot_step=self.parameters.graphing_interval,
                                              x_lenght=1000, enable_legend=True,
                                              x_name="time [s]",
                                              y_name="v [m/s], d [m], F [N]")
        self.rk_graph.add_plotline("Velocity",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.rk_graph.add_plotline("Displacement",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.rk_graph.add_plotline("Force",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="blue")
        self.rk_graph.set_text(title="Spring-mass-damper Runge-Kutta 4")

        self.tz_graph = None
        self.fe_graph = None
        self.create_tz_fe_graphs()

        self.show_dropdown = QComboBox(self)
        self.show_dropdown.addItem("All")
        self.show_dropdown.addItem("RK4")
        self.show_dropdown.activated.connect(self.graph_show_selected)

        self.simulation_view_layout.addWidget(self.rk_graph,0,0,1,1)
        self.simulation_view_layout.addWidget(self.tz_graph,1,0,1,1)
        self.simulation_view_layout.addWidget(self.fe_graph,2,0,1,1)
        self.simulation_view_layout.addWidget(self.show_dropdown,3,0,1,1)

        self.setLayout(self.simulation_view_layout)


    def create_tz_fe_graphs(self):
        '''creates graphs for trapezoidal method and forward euler'''
        self.tz_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                              plot_step=self.parameters.graphing_interval,
                                              x_lenght=1000, enable_legend=True,
                                              x_name="time [s]",
                                              y_name="v [m/s], d [m], F [N]")
        self.tz_graph.add_plotline("Velocity",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.tz_graph.add_plotline("Displacement",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.tz_graph.add_plotline("Force",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="blue")
        self.tz_graph.set_text(title="Spring-mass-damper Trapezoidal approximation")

        self.fe_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                              plot_step=self.parameters.graphing_interval,
                                              x_lenght=1000, enable_legend=True,
                                              x_name="time [s]",
                                              y_name="v [m/s], d [m], F [N]")
        self.fe_graph.add_plotline("Velocity",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.fe_graph.add_plotline("Displacement",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.fe_graph.add_plotline("Force",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="blue")
        self.fe_graph.set_text(title="Spring-mass-damper forward Euler")


    def graph_show_selected(self):
        '''actions of selecting viewed graphs'''
        state = self.show_dropdown.currentIndex()
        if state == 0:
            self.simulation_view_layout.addWidget(self.rk_graph,0,0,1,1)
            self.create_tz_fe_graphs()
            self.simulation_view_layout.addWidget(self.tz_graph,1,0,1,1)
            self.simulation_view_layout.addWidget(self.fe_graph,2,0,1,1)
            setattr(simulator,"shown_graphs",1)
        else:
            self.simulation_view_layout.removeWidget(self.tz_graph)
            self.tz_graph.deleteLater()
            self.tz_graph = None
            self.simulation_view_layout.removeWidget(self.fe_graph)
            self.fe_graph.deleteLater()
            self.fe_graph = None
            self.simulation_view_layout.addWidget(self.rk_graph,0,0,3,1)
            setattr(simulator,"shown_graphs",0)


    @Slot(list)
    def update(self, inp):
        '''update Slot method is run once every graphing interval.
           Should contain updates of all visual elements.
           Data from simulator is contained in input variable with default name "inp".
           inp is a type=list and the data is in the same order it is send from the simulator
           as "send_to_graph function call.
           last line of the method must be call for self.graphing_flow_control()'''

        self.rk_graph.step("Displacement",inp[0][0][1])
        self.rk_graph.step("Velocity",inp[0][0][0])
        self.rk_graph.step("Force",inp[0][1][0])

        if inp[4]:
            self.tz_graph.step("Displacement",inp[1][0][1])
            self.tz_graph.step("Velocity",inp[1][0][0])
            self.tz_graph.step("Force",inp[1][1][0])

            self.fe_graph.step("Displacement",inp[2][0][1])
            self.fe_graph.step("Velocity",inp[2][0][0])
            self.fe_graph.step("Force",inp[2][1][0])

        if inp[3][0]:
            self.rk_graph.steptime = inp[3][1]
            if inp[4]:
                self.tz_graph.steptime = inp[3][1]
                self.fe_graph.steptime = inp[3][1]

        ### LAST LINE OF UPDATE METHOD
        self.graphing_flow_control()
        ### LAST LINE OF UPDATE METHOD
