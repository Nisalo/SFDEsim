
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
from SimulationWindowWidgets import ParameterViewWidget, PictureViewWidget
from SimuMath import (cart2pol, angle_loop_rad, pol2cart, solve_2bus_NR, solve_power_flow_GS)



class parameters():
    '''parameters object is used to declare and contain simualtion parameters and
       input vaiables.
       Required parameters: simulation_name, steptime, simulation_time, graphing_interval
       The input variables are declared in input_parameters dictionary.'''
    def __init__(self):

        self.simulation_name = "Example simulation"
        self.steptime = 0.00001
        self.simulation_time = 0
        self.graphing_interval = 10     # graphs are only redrawn every xth step to reduce load


        self.input_parameters = {
            "parameter1":{
                "display_name": "Parameter 1",
                "symbol": "",
                "editable": True,
                "type": "number",
                "init_value": 10,
                "unit": "",
                "default_prefix": 3,
                "prefix_limits": [0,3],
                "maximum":150*(10**3),
                "minimum": 0
            },
            "parameter2":{
                "display_name": "Parameter 2",
                "symbol": "",
                "editable": False,
                "type": "number",
                "init_value": 50,
                "unit": "",
                "default_prefix": 0,
                "prefix_limits": [-6,3],
                "maximum":1000,
                "minimum": 0
            },
            "paramter3":{
                "display_name": "Parameter 3",
                "symbol": "",
                "editable": True,
                "type": "dropdown",
                "items": ["choice1", "choice2", "choice3"],
                "unit": ""
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

        ### Do not change ###
        # initializes some classes and methods for use in the simulator object
        self.params = params
        self.signals = signals
        self.flow_control = parent.simulation_flow_control
        self.send_to_graph = send_to_graph
        ### Do not change ###


        # initializes the numeric input variables
        self.input_variables = np.array(
            [self.params.input_parameters["parameter1"]["init_value"],#0
             self.params.input_parameters["parameter2"]["init_value"],#1
             ], dtype=float
        )


        ### Do not change ###
        # Sets up the correct default prefixes for all numeric inputs
        i = 0
        for _, var in enumerate(self.params.input_parameters.keys()):
            if self.params.input_parameters[var]["type"] == "number":
                self.input_variables[i] *= 10**self.params.input_parameters[var]["default_prefix"]
                i += 1
        ## Do not change ###


        # initializes the dropdown varibles
        self.input_texts = [
             self.params.input_parameters["parameter3"]["items"][0]
        ]

        # Variables which are only set manually at launch can be declared here
        # self.variable_x = 14
        # self.variable_y = 3
        # self.variable_z = 24*self.variable_y+self.variable_x


        # Do not change
        self.update_matrixes()
        # Do not change



    def update_matrixes(self):
        '''Function is executed after updating inputs either by user clicking the update button,
           or by changing input varibles when autoupdate is on. 
           Additionally fun at startup.
           This fuction should include all calculations not necessary to run every cycle but after 
           user action.'''


        # calculations and varible changes done when update button is pressed here
        
        # self.variable_a = self.variable_x+self.varible_y

        # self.variable_b = self.variable_x*self.input_variables[1]

        # if self.input_texts[0] == "choice1"
        #   self.variable_c = self.input_variables[0] * -1
        # elif self.input_texts[0] == "choice2"
        #   self.variable_c = self.input_variables[0] * 1
        # elif self.input_texts[0] == "choice3"
        #   self.variable_c = 0
        # 





    @Slot(bool)
    def run(self, _):
        '''Simulation calculation method. 
        This method shoud include simulation step calculation and method for sending data to graph.
        Calculation loop is run as long as simulation is set ON by user.
        Data is sent to the graph via self.send_to_graph() function which should be called at the
        end of the method. This fucntion takes 1 input type=list, which should contain all data to
        be send for graphs or other visual elements in graphicsViewWidget'''
        while self.flow_control():
            # calculations done at every simulation step here

            # variable_i = self.variable_a self.variable_z

            # variable_j = self.variable_c-self.variable_x

            # variable_k = (self.variable_a*self.variable_j) / self.variable_b
            



            # data sending to graphs
            self.send_to_graph([#variable_i,
                                #variable_j,
                                #variable_k,
                                #variable_a,
                                #variable_b
                                #variable_c
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
        ### Do not change ###
        self.parameters = params
        self.graphing_flow_control = graphing_flow_control
        ### Do not change ###

        # example on creating layout
        self.simulation_view_layout = QGridLayout()
        # width of parameter view can be manually set
        parent.parameter_view_size = 220

        # example of time domain plot
        self.example_line_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                plot_step=self.parameters.graphing_interval,
                                x_lenght=1000, enable_legend=True,
                                x_name="name of x-axis", y_name="name of y-axis")
        # example of adding plot to time domain graph
        # the x and y data can be set to any default values, in this exmple the initial line willbe set to y=0
        self.example_line_graph.add_plotline("variable_i",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red", linetype="..")
        # graph name can be set as shown
        self.example_line_graph.set_text(title="Voltages and current")
        # plotline linetype type can be changed as shown
        # for line type '-'=continuous, '--'=dashed, '..'=dotted
        self.example_line_graph.change_line_pen("variable_i",width=2)

        # example of phasor domain plot
        self.example_phasor_graph = PhasorGraphWidget("example phasors","x","y")
        # add phasor to the plot
        self.example_phasor_graph.add_phasor("variable_j",1,1, color="green")
        # phasor linetype type can be changed as shown
        # for line type '-'=continuous, '--'=dashed, '..'=dotted
        self.example_phasor_graph.change_line_pen("variable_j",width=2)


        # example on numeric parameter view
        self.example_parameter_view = ParameterViewWidget("Example_header")
        # add data rows as shown
        self.example_parameter_view.add_row("variable_i",0,"example_unit")
        self.example_parameter_view.add_row("variable_j",10,"example_unit")
        self.example_parameter_view.add_row("variable_k",3,"example_unit")
        #separator line can be added as shown
        self.example_parameter_view.add_line()
        self.example_parameter_view.add_row("variable_a",0,"example_unit")
        self.example_parameter_view.add_row("variable_b",0,"example_unit")
        self.example_parameter_view.add_row("variable_c",0,"example_unit")

        # example on adding a picture
        self.example_image = PictureViewWidget("example_picture.png")


        # created widgets has to placed into the created layout
        # this example creates 2-by-2 grid layout
        self.simulation_view_layout.addWidget(self.example_line_graph,0,0,1,1)
        self.simulation_view_layout.addWidget(self.example_phasor_graph,0,1,1,1)
        self.simulation_view_layout.addWidget(self.example_parameter_view,1,0,1,1)
        self.simulation_view_layout.addWidget(self.example_image,1,1,1,1)

        # the created layot is set as shown
        self.setLayout(self.simulation_view_layout)



    @Slot(list)
    def update(self, inp):
        '''update Slot method is run once every graphing interval.
           Should contain updates of all visual elements.
           Data from simulator is contained in input variable with default name "inp".
           inp is a type=list and the data is in the same order it is send from the simulator
           as "send_to_graph function call.
           last line of the method must be call for self.graphing_flow_control()'''

        # time domain graphs are best updated with "step" method, which only appends the last step
        self.example_line_graph.step("variable_i",inp[0])
        # phasor domain graphs are updated using "update" method
        self.example_phasor_graph.update("variable_j",inp[1],0)


        # parameter view can be updated with "update_row", "update_complex_row" or "update_polar_row"
        # depending on the type of value to be updated
        self.example_parameter_view.update_row(0,inp[0])
        self.example_parameter_view.update_complex_row(1,inp[1])
        self.example_parameter_view.update_polar_row(2,inp[2],0)

        self.example_parameter_view.update_row(3,inp[3])
        self.example_parameter_view.update_complex_row(4,inp[4])
        self.example_parameter_view.update_complex_row(5,inp[5])




        ### LAST LINE OF UPDATE METHOD, DO NOT EDIT OR ADD CODE AFTER
        self.graphing_flow_control()
        ### LAST LINE OF UPDATE METHOD, DO NOT EDIT OR ADD CODE AFTER
        # This allows simulator to progress to the next graphing step
