
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
from PhasorPlotWidget import PhasorGraphWidget
from LinePlotWidget import LinePlotWidget
from SimuMath import angle_loop_rad, np_abc_to_alpha_beta, np_alpha_beta_to_dq



class parameters():
    def __init__(self):

        self.simulation_name = "Reference frame simulation"
        self.steptime = 0.000025
        self.simulation_time = 0
        self.data_length = 50000
        self.graphing_interval = 10


        self.input_parameters = {
            "freq":{
                "display_name": "Frequency",
                "symbol": "f",
                "editable": True,
                "type": "number",
                "init_value": 50,
                "unit": "Hz",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":100,
                "minimum": 1*10**-1
            },
            "phase_a_amplitude":{
                "display_name": "Amplitude a",
                "symbol": "V_1",
                "editable": True,
                "type": "number",
                "init_value": 1,
                "unit": "p.u.",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":10,
                "minimum": 0
            },
            "phase_b_amplitude":{
                "display_name": "Amplitude b",
                "symbol": "V_2",
                "editable": True,
                "type": "number",
                "init_value": 1,
                "unit": "p.u.",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":10,
                "minimum": 0
            },
            "phase_c_amplitude":{
                "display_name": "Amplitude c",
                "symbol": "V_3",
                "editable": True,
                "type": "number",
                "init_value": 1,
                "unit": "p.u.",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":10,
                "minimum": 0
            }
        }


class simulator(QObject):
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
            [params.input_parameters["freq"]["init_value"],
             params.input_parameters["phase_a_amplitude"]["init_value"],
             params.input_parameters["phase_b_amplitude"]["init_value"],
             params.input_parameters["phase_c_amplitude"]["init_value"]
             ], dtype=float
        )

        i = 0
        for _, var in enumerate(self.params.input_parameters.keys()):
            if self.params.input_parameters[var]["type"] == "number":
                self.input_variables[i] *= 10**self.params.input_parameters[var]["default_prefix"]
                i += 1

        self.input_texts = [
             
        ]

        self.albet = np.array([0,0],dtype=float)

        self.dq = np.array([0,0],dtype=float)

        self.angle = 0

        self.update_matrixes()


    def update_matrixes(self):
        self.abc = np.array(
            [0,
             0,
             0], dtype=float
        )

        self.albet = np.array(
            [0,
             0
            ], dtype=float
        )

        self.dq = np.array(
            [0,
             0
            ], dtype=float
        )

        self.phasor1 = np.array(
            [0,
             0,
             0,
             0,
             0,
             0
            ], dtype=float
        )

        self.phasor2 = np.array(
            [0,
             0,
             0,
             0,
             0,
             0
            ], dtype=float
        )


        self.frequency = self.input_variables[0]
        self.amplitude_a = self.input_variables[1]
        self.amplitude_b = self.input_variables[2]
        self.amplitude_c = self.amplitude_a


    @Slot(bool)
    def run(self, _):
        '''Simulation calculation method. 
        This method shoud include simulation step calculation and method for sending data to graph.
        Calculation loop is run as long as simulation is set ON by user.
        Data is sent to the graph via self.send_to_graph() function which should be called at the
        end of the method. This fucntion takes 1 input type=list, which should contain all data to
        be send for graphs or other visual elements in graphicsViewWidget'''
        while self.flow_control():

            ang = ((np.pi*2)/((1/self.frequency)/self.params.steptime))
            self.angle += ang
            self.angle = angle_loop_rad(self.angle)

            y1 = float(np.sin(self.angle)*self.amplitude_a)
            x1 = float(np.cos(self.angle)*self.amplitude_a)
            y2 = float(np.sin((self.angle-2*np.pi/3))*self.amplitude_b)
            x2 = float(np.cos((self.angle-2*np.pi/3))*self.amplitude_b)
            y3 = float(np.sin((self.angle-4*np.pi/3))*self.amplitude_c)
            x3 = float(np.cos((self.angle-4*np.pi/3))*self.amplitude_c)

            self.abc[0] = y1
            self.abc[1] = y2
            self.abc[2] = y3

            self.phasor1[0] = y1
            self.phasor1[1] = x1
            self.phasor1[2] = y2
            self.phasor1[3] = x2
            self.phasor1[4] = y3
            self.phasor1[5] = x3

            self.albet = np_abc_to_alpha_beta(self.abc)

            self.dq = np_alpha_beta_to_dq(self.albet,
                                      np.arctan2(self.albet[1],self.albet[0]))

            self.phasor2[0] = y1*np.cos(0)
            self.phasor2[1] = y1*np.sin(0)
            self.phasor2[2] = y2*np.cos(2*np.pi/3)+self.phasor2[0]
            self.phasor2[3] = y2*np.sin(2*np.pi/3)+self.phasor2[1]
            self.phasor2[4] = y3*np.cos(4*np.pi/3)+self.phasor2[2]
            self.phasor2[5] = y3*np.sin(4*np.pi/3)+self.phasor2[3]


            self.send_to_graph([self.phasor1,
                                self.albet,
                                self.dq,
                                self.phasor2
                                ])



class graphicsViewWidget(QWidget):
    '''Simulation graphics containment widdget.
       This widget is placed as central widget in the window.
       The definition and placements of all visual objects should be done in __init__ method, 
       including graphs, pictures, variable views, buttons etc.
       The update Slot method is run once every graphing interval defined in parameter object
       and should contain updates of all visual objects'''
    def __init__(self, parent, params, graphing_flow_control):
        super().__init__()

        self.parameters = params
        self.graphing_flow_control = graphing_flow_control

        self.simulation_view_layout = QGridLayout()
        parent.parameter_view_size = 150

        init_phase_angle = 2*np.pi/3
        x = np.cos(init_phase_angle)
        y = np.sin(init_phase_angle)

        self.graph = PhasorGraphWidget("Frames as phasors","x","y")
        self.graph.add_phasor("Phasor1",1,0)
        self.graph.add_phasor("Phasor2",x,y)
        self.graph.add_phasor("Phasor3",x,-y)
        self.graph.add_phasor("Alpha1",1,0, color="red")
        self.graph.add_phasor("Beta1",0.0001,1, color="red")
        self.graph.add_phasor("d1",1,0, color="blue")
        self.graph.add_phasor("q1",0.0001,1, color="blue")

        self.graph.change_phasor_pen("Phasor1", width=2)
        self.graph.change_phasor_pen("Phasor2", width=2)
        self.graph.change_phasor_pen("Phasor3", width=2)
        self.graph.change_phasor_pen("Alpha1", linetype="..",width=2)
        self.graph.change_phasor_pen("Beta1", linetype="..",width=2)

        self.phasor_graph2 = PhasorGraphWidget("Phase components","x","y")
        self.phasor_graph2.add_phasor("L1_V",1,0,color="red")
        self.phasor_graph2.add_phasor("L2_V",1,0,color="green")
        self.phasor_graph2.add_phasor("L3_V",1,0,color="blue")
        self.phasor_graph2.add_phasor("L1_T",1,0,color="red")
        self.phasor_graph2.add_phasor("L2_T",1,0,color="green")
        self.phasor_graph2.add_phasor("L3_T",1,0,color="blue")
        self.phasor_graph2.add_phasor("Total",1,0,color="magenta")
        self.phasor_graph2.change_phasor_pen("L1_T",width=2)
        self.phasor_graph2.change_phasor_pen("L2_T",width=2)
        self.phasor_graph2.change_phasor_pen("L3_T",width=2)
        self.phasor_graph2.change_phasor_pen("Total",width=2)
        self.phasor_graph2.change_phasor_pen("L1_V",linetype="..",width=2)
        self.phasor_graph2.change_phasor_pen("L2_V",linetype="..",width=2)
        self.phasor_graph2.change_phasor_pen("L3_V",linetype="..",width=2)

        self.lin_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                              plot_step=self.parameters.graphing_interval,
                                              x_lenght=1000, enable_legend= True)
        self.lin_graph.add_plotline("L1",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.lin_graph.add_plotline("L2",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.lin_graph.add_plotline("L3",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="blue")
        self.lin_graph.change_line_pen("L1", width=2)
        self.lin_graph.change_line_pen("L2", width=2)
        self.lin_graph.change_line_pen("L3", width=2)
        self.lin_graph.set_text(title="ABC frame")

        self.lin_graph2 = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                             plot_step=self.parameters.graphing_interval,
                                             x_lenght=1000, enable_legend= True)
        self.lin_graph2.add_plotline("Alpha",x_data=np.array([0,1,2]),
                                     y_data=np.array([0,0,0]),color="red")
        self.lin_graph2.add_plotline("Beta",x_data=np.array([0,1,2]),
                                     y_data=np.array([0,0,0]),color="green")
        self.lin_graph2.change_line_pen("Alpha", width=2)
        self.lin_graph2.change_line_pen("Beta", width=2)
        self.lin_graph2.set_text(title="Alpha-beta frame")

        self.lin_graph3 = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                             plot_step=self.parameters.graphing_interval,
                                             x_lenght=1000, enable_legend= True)
        self.lin_graph3.add_plotline("d",x_data=np.array([0,1,2]),
                                     y_data=np.array([0,0,0]),color="red")
        self.lin_graph3.add_plotline("q",x_data=np.array([0,1,2]),
                                     y_data=np.array([0,0,0]),color="green")
        self.lin_graph3.change_line_pen("d", width=2)
        self.lin_graph3.change_line_pen("q", width=2)
        self.lin_graph3.set_text(title="dq frame")


        self.simulation_view_layout.addWidget(self.lin_graph,0,0, 2,1)
        self.simulation_view_layout.addWidget(self.lin_graph2,2,0, 2,1)
        self.simulation_view_layout.addWidget(self.lin_graph3,4,0, 2,1)

        self.simulation_view_layout.addWidget(self.graph,0,1, 3,2)
        self.simulation_view_layout.addWidget(self.phasor_graph2,3,1, 3,2)

        self.setLayout(self.simulation_view_layout)


    @Slot(list)
    def update(self, inp):
        '''update Slot method is run once every graphing interval.
           Should contain updates of all visual elements.
           Data from simulator is contained in input variable with default name "inp".
           inp is a type=list and the data is in the same order it is send from the simulator
           as "send_to_graph function call.
           last line of the method must be call for self.graphing_flow_control()'''

        y1 = inp[0][0]
        x1 = inp[0][1]
        y2 = inp[0][2]
        x2 = inp[0][3]
        y3 = inp[0][4]
        x3 = inp[0][5]
        alpha_beta = inp[1]
        d_q = inp[2]
        yt1 = inp[3][1]
        xt1 = inp[3][0]
        yt2 = inp[3][3]
        xt2 = inp[3][2]
        yt3 = inp[3][5]
        xt3 = inp[3][4]

        self.graph.update("Phasor1",x1,y1)
        self.graph.update("Phasor2",x2,y2)
        self.graph.update("Phasor3",x3,y3)

        self.graph.update("Alpha1",x1,alpha_beta[0])
        self.graph.update("Beta1",-alpha_beta[0],-alpha_beta[1])

        self.graph.update("d1",d_q[0],d_q[1])
        self.graph.update("q1",d_q[1],d_q[0])

        self.phasor_graph2.update("L1_V",y1*np.cos(0),y1*np.sin(0))
        self.phasor_graph2.update("L2_V",y2*np.cos(2*np.pi/3),y2*np.sin(2*np.pi/3))
        self.phasor_graph2.update("L3_V",y3*np.cos(4*np.pi/3),y3*np.sin(4*np.pi/3))
        self.phasor_graph2.update("L1_T",xt1,yt1)
        self.phasor_graph2.update("L2_T",xt2,yt2,xt1,yt1)
        self.phasor_graph2.update("L3_T",xt3,yt3,xt2,yt2)
        self.phasor_graph2.update("Total",xt3,yt3)

        self.lin_graph.step("L1",y1)
        self.lin_graph.step("L2",y2)
        self.lin_graph.step("L3",y3)

        self.lin_graph2.step("Alpha",alpha_beta[0])
        self.lin_graph2.step("Beta",alpha_beta[1])

        self.lin_graph3.step("d",d_q[0])
        self.lin_graph3.step("q",d_q[1])

        ### LAST LINE OF UPDATE METHOD
        self.graphing_flow_control()
        ### LAST LINE OF UPDATE METHOD

