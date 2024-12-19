
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
from PySide6.QtWidgets import (QGridLayout, QWidget, QLabel, QComboBox)
import numpy as np
parent_directory = os.path.abspath('../Z_DI_Simulator')
sys.path.append('..')
from PhasorPlotWidget import PhasorGraphWidget
from LinePlotWidget import LinePlotWidget
from SimulationWindowWidgets import ParameterViewWidget, PictureViewWidget
from SimuMath import (cart2pol, angle_loop_rad, pol2cart, solve_2bus_NR, solve_power_flow_GS)



cable_list = {"---": [-1,-1],
              "3x50Al+35Cu":  [0.641, 0.00046],
              "3x95Al+35Cu":  [0.320, 0.00040],
              "3x120Al+35Cu": [0.253, 0.00039],
              "3x150Al+35Cu": [0.206, 0.00037],
              "3x185Al+35Cu": [0.164, 0.00036],
              "3x240Al+70Cu": [0.125, 0.00035],
              "3x300Al+70Cu": [0.100, 0.00034],
              "Turkey (ACSR)": [0.655, 1.27*10**-6],
              "Swan (ACSR)": [0.412, 1.22*10**-6],
              "Sparrow (ACSR)" : [0.259, 1.18*10**-6],
              "Robin (ACSR)": [0.206, 1.15*10**-6],
              "Raven (ACSR)": [0.163, 1.13*10**-6],
              "Pigeon (ACSR)": [0.103, 1.08*10**-6]
              }


def set_current_cable(ind):
    name = list(cable_list.keys())[ind]
    setattr(simulator,"cable_impedances",cable_list[name])


class parameters():
    '''parameters object is used to declare and contain simualtion parameters and
       input vaiables.
       Required parameters: simulation_name, steptime, simulation_time, graphing_interval
       The input variables are declared in input_parameters dictionary.'''
    def __init__(self):

        self.simulation_name = "Voltage drop simulation"
        self.steptime = 0.00001
        self.simulation_time = 0
        self.graphing_interval = 10     # graphs are only redrawn every xth step to reduce load


        self.input_parameters = {
            "u_in":{
                "display_name": "Grid line voltage",
                "symbol": "U_g_r_i_d",
                "editable": True,
                "type": "number",
                "init_value": 20,
                "unit": "V",
                "default_prefix": 3,
                "prefix_limits": [0,3],
                "maximum":150*(10**3),
                "minimum": 0
            },
            "frequency":{
                "display_name": "Frequency",
                "symbol": "f",
                "editable": True,
                "type": "number",
                "init_value": 50,
                "unit": "Hz",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":100,
                "minimum": 0
            },
            "line_length":{
                "display_name": "Line length",
                "symbol": "l",
                "editable": True,
                "type": "number",
                "init_value": 10.0,
                "unit": "km",
                "default_prefix": 0,
                "prefix_limits": [0,0],
                "maximum":1000,
                "minimum": 0.1
            },
            "line_resistance":{
                "display_name": "Line resistance",
                "symbol": "R_l_i_n_e",
                "editable": True,
                "type": "number",
                "init_value": 0.337,
                "unit": "Ω/km",
                "default_prefix": 0,
                "prefix_limits": [-3,0],
                "maximum":100,
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
                "maximum":100,
                "minimum": 0
            },
            "load_power":{
                "display_name": "Load power",
                "symbol": "P_l_o_a_d",
                "editable": True,
                "type": "number",
                "init_value": 6000000,
                "unit": "W",
                "default_prefix": 0,
                "prefix_limits": [0,6],
                "maximum": 1*(10**9),
                "minimum": 0
            },
            "load_cos_phi":{
                "display_name": "Cos(φ)",
                "symbol": "",
                "editable": True,
                "type": "number",
                "init_value": 0.85,
                "unit": "",
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
            "conductance":{
                "display_name": "Shunt conductance",
                "symbol": "G_l_i_n_e",
                "editable": False,
                "type": "number",
                "init_value": 0,
                "unit": "S/km",
                "default_prefix": -6,
                "prefix_limits": [-9,0],
                "maximum": 1000,
                "minimum": 0
            },
            "capacitance":{
                "display_name": "Shunt capacitance",
                "symbol": "C_l_i_n_e",
                "editable": False,
                "type": "number",
                "init_value": 0,
                "unit": "F/km",
                "default_prefix": -6,
                "prefix_limits": [-9,0],
                "maximum": 1000,
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
    cable_impedances = [-1,-1]
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
             self.params.input_parameters["frequency"]["init_value"],#1
             self.params.input_parameters["line_length"]["init_value"],#2
             self.params.input_parameters["line_resistance"]["init_value"],#3
             self.params.input_parameters["line_inductance"]["init_value"],#4
             self.params.input_parameters["load_power"]["init_value"],#5
             self.params.input_parameters["load_cos_phi"]["init_value"],#6
             # advanced
             self.params.input_parameters["conductance"]["init_value"],#7
             self.params.input_parameters["capacitance"]["init_value"]#8
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

        self.I_total = 0
        self.U_send = 0
        self.U_r = 0
        self.U_h = 0
        self.progress_bar_index = 0

        self.pi2 = 2*np.pi
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

        self.inputs_updated = True
        self.iter_number = 700          # maximum number of iterations
        self.phasors_update = self.params.graphing_interval+1

        self.U_send = self.input_variables[0]       #sending end voltage
        self.frequency = self.input_variables[1]
        self.cos_phi = self.input_variables[6]
        if self.cos_phi >= 1:
            self.cos_phi = 0.9999999
        # load power computation
        self.P_load = self.input_variables[5]
        self.S_load = np.abs(self.P_load/abs(self.cos_phi))
        if self.input_texts[0] == "ind.":
            self.Q_load = np.sqrt(self.S_load**2-self.P_load**2)
        elif self.input_texts[0] == "cap.":
            self.Q_load = -np.sqrt(self.S_load**2-self.P_load**2)
        self.S_load_complex = self.P_load+self.Q_load*1j

        self.line_len = self.input_variables[2]     #length of the line [km]

        # depending on if cable type is selected or if R and L are given directly, the computation of
        # line R and X_L are different  
        if getattr(simulator,"cable_impedances")[0] == -1:
            self.r_line = self.input_variables[3]*self.input_variables[2]
            self.x_line = self.input_variables[4]*2*np.pi*self.frequency*self.input_variables[2]
        else:
            self.r_line = getattr(simulator,"cable_impedances")[0]*self.input_variables[2]
            self.x_line = getattr(simulator,"cable_impedances")[1]*self.input_variables[2]
            
        if self.r_line <= 0:
            message = "Line resistance cannot be zero or less"
            self.signals.simulation_error.emit([message,
                                                "Parameter error"])

        #  line shunt conductance and capacitance
        self.g = self.input_variables[7]
        self.b = self.input_variables[8]

        # line longtudal Z and shunt Y
        self.Z = self.r_line+self.x_line*1j
        self.Y = self.g+self.b*1j

        # Y-bus formulation
        Y_00 = (1/self.Z)+(self.Y/2)
        Y_01 = -(1/self.Z)
        Y_bus = np.array([[Y_00,Y_01],[Y_01,Y_00]],dtype=complex)

        # inital voltage guess for the receiving end
        U2_guess = self.U_send
        delta_2 = -np.arcsin((self.P_load*np.imag(self.Z))/(self.U_send*U2_guess))

        # Apparent power vector for iterator
        S_vector = np.array([0,(self.S_load_complex)*-1],dtype=complex)

        # bus data
        n_bus = 2
        slack_bus = 1
        # U vector for iterator
        U_vector = np.array(np.zeros((n_bus,)),dtype=complex)
        U_vector[slack_bus-1] = self.U_send
        U_vector[1] = pol2cart(U2_guess,delta_2*0.1)[0]-pol2cart(U2_guess,delta_2*0.1)[1]*1j
        
        # receiving end voltage iteration 
        self.U_r = solve_2bus_NR(Y_bus,U_vector,S_vector,1,self.iter_number)
        self.Ur_GS = solve_power_flow_GS(Y_bus,slack_bus,U_vector,S_vector,1,self.iter_number)
        # error handling for iterator convergence
        if np.isnan(self.U_r):
            message = "Receiving end voltage calculation does not converge\n"
            message += "Selected power cannot be supplied with given grid voltage\n "
            message += "and line parameters"
            self.signals.simulation_error.emit([message,
                                                "Convergence error"])
        # voltage loss
        self.U_h = self.U_send-self.U_r
        # system current
        self.I_total = np.conjugate(self.S_load_complex/(np.sqrt(3)*self.U_r))



    @Slot(bool)
    def run(self, _):
        '''Simulation calculation method. 
        This method shoud include simulation step calculation and method for sending data to graph.
        Calculation loop is run as long as simulation is set ON by user.
        Data is sent to the graph via self.send_to_graph() function which should be called at the
        end of the method. This fucntion takes 1 input type=list, which should contain all data to
        be send for graphs or other visual elements in graphicsViewWidget'''
        while self.flow_control():
            # phase angles
            self.angle_steps = (self.pi2/((1/self.frequency)/self.params.steptime))
            self.phase_angles += self.angle_steps
            self.phase_angles[0] = angle_loop_rad(self.phase_angles[0])

            # RMS, amplitudes and angles 
            U_S_rms = np.abs(self.U_send)
            U_S_amp = U_S_rms*np.sqrt(2)
            U_S_ang = self.phase_angles
            U_R_rms = np.abs(self.U_r)
            U_R_amp = U_R_rms*np.sqrt(2)
            U_R_ang = self.phase_angles+cart2pol(np.real(self.U_r),np.imag(self.U_r))[1]

            # phasor graphs are only updated when inputs are updated to reduce graphical load
            if self.phasors_update >= 0:
                update_phasors = True
            else:
                update_phasors = False

            # data sending to graphs
            self.send_to_graph([U_S_amp,#0
                                U_S_rms,#1
                                U_S_ang,#2
                                U_R_amp,#3
                                U_R_rms,#4
                                U_R_ang,#5
                                self.U_r,#6
                                self.U_h,#7
                                self.I_total,#8
                                update_phasors,#9
                                self.Z
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

        self.simulation_view_layout = QGridLayout()
        parent.parameter_view_size = 220

        self.voltage_graph = LinePlotWidget(simu_steptime=self.parameters.steptime,
                                plot_step=self.parameters.graphing_interval,
                                x_lenght=1000, enable_legend=True,
                                x_name="time [s]", y_name="voltage [V], current*10 [A]")
        self.voltage_graph.add_plotline("U Grid",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="red")
        self.voltage_graph.add_plotline("U Load",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="green")
        self.voltage_graph.add_plotline("I*10",x_data=np.array([0,1,2]),
                                    y_data=np.array([0,0,0]),color="magenta")
        self.voltage_graph.set_text(title="Voltages and current")
        self.voltage_graph.change_line_pen("U Grid",width=2)
        self.voltage_graph.change_line_pen("U Load",width=2)
        self.voltage_graph.change_line_pen("I*10",width=2)

        self.U_phasor_graph = PhasorGraphWidget("Voltage phasors","x","y")
        self.U_phasor_graph.add_phasor("U_load",1,1, color="green")
        self.U_phasor_graph.add_phasor("U_grid",1,1, color="red")
        self.U_phasor_graph.add_phasor("U_loss",1,1, color="cyan")
        self.U_phasor_graph.add_phasor("U_loss_r",1,1, color="blue")
        self.U_phasor_graph.add_phasor("U_loss_x",1,1, color="black")
        self.U_phasor_graph.change_phasor_pen("U_load",width=1.5)
        self.U_phasor_graph.change_phasor_pen("U_grid",width=1.5)
        self.U_phasor_graph.change_phasor_pen("U_loss",width=1.5)
        self.U_phasor_graph.change_phasor_pen("U_loss_r",width=1.5)
        self.U_phasor_graph.change_phasor_pen("U_loss_x",width=1.5)

        self.I_phasor_graph = PhasorGraphWidget("Current phasor","x","y")
        self.I_phasor_graph.add_phasor("I_system",1,1, color="magenta")
        self.I_phasor_graph.change_phasor_pen("I_system",width=1.5)


        self.parameter_view = ParameterViewWidget("Parameters")
        self.parameter_view.add_row("Grid voltage (rms)",0,"V")
        self.parameter_view.add_row("Grid voltage",0,"V")
        self.parameter_view.add_row("Grid voltage",0,"V")
        self.parameter_view.add_line()
        self.parameter_view.add_row("Load voltage (rms)",0,"V")
        self.parameter_view.add_row("Load voltage",0,"V")
        self.parameter_view.add_row("Load voltage",0,"V")
        self.parameter_view.add_line()
        self.parameter_view.add_row("Voltage drop (rms)",0,"V")
        self.parameter_view.add_row("Voltage drop",0,"V")
        self.parameter_view.add_row("Voltage drop",0,"V")
        self.parameter_view.add_line()
        self.parameter_view.add_row("Current (rms)",0,"A")
        self.parameter_view.add_row("Current",0,"A")
        self.parameter_view.add_row("Current",0,"A")
        self.parameter_view.add_line()
        self.parameter_view.add_row("Line impedance",0,"Ω")

        self.image = PictureViewWidget("voltage_drop_and_losses.png")


        self.cable_name_label = QLabel(self)
        self.cable_name_label.setText("Cable type:")
        self.cable_selection = QComboBox(self)
        for cable in cable_list.keys():
            self.cable_selection.addItem(cable)
        self.cable_selection.activated.connect(set_current_cable)


        self.simulation_view_layout.addWidget(self.image,0,0,1,2)
        self.simulation_view_layout.addWidget(self.parameter_view,0,2,1,1)
        self.simulation_view_layout.addWidget(self.U_phasor_graph,0,4,1,3)
        self.simulation_view_layout.addWidget(self.cable_name_label,1,0,1,1)
        self.simulation_view_layout.addWidget(self.cable_selection,1,1,1,1)
        self.simulation_view_layout.addWidget(self.voltage_graph,2,0,1,3)
        self.simulation_view_layout.addWidget(self.I_phasor_graph,2,4,1,3)

        self.setLayout(self.simulation_view_layout)


    @Slot(list)
    def update(self, inp):
        '''update Slot method is run once every graphing interval.
           Should contain updates of all visual elements.
           Data from simulator is contained in input variable with default name "inp".
           inp is a type=list and the data is in the same order it is send from the simulator
           as "send_to_graph function call.
           last line of the method must be call for self.graphing_flow_control()'''

        self.voltage_graph.step("U Grid",inp[0]*np.cos(inp[2][0]))
        self.voltage_graph.step("U Load",inp[3]*np.cos(inp[5][0]))
        I_ang = np.tan(np.imag(inp[8])/np.real(inp[8]))
        self.voltage_graph.step("I*10",10*np.abs(inp[8])*(np.cos(inp[2][0]+I_ang)))

        # numeric parameters and phasor graphs are only updated when inputs are updated to reduce
        # computational load
        if inp[9]:
            x_Ur = np.real(inp[6])
            y_Ur = np.imag(inp[6])
            x_r_loss = x_Ur+np.real(inp[7])
            y_r_loss = y_Ur+np.imag(inp[7])
            U_r_ang = np.tan(np.imag(inp[6])/np.real(inp[6]))*-1
            y_U_rh = np.real(inp[7])*np.sin(U_r_ang)
            x_U_rh = inp[1]-np.real(inp[7])*np.cos(U_r_ang)

            i = 0
            self.parameter_view.update_row(i,inp[1])
            i += 1
            self.parameter_view.update_complex_row(i,inp[1]+0j)
            i += 1
            self.parameter_view.update_polar_row(i,inp[1],0)
            i += 1
            self.parameter_view.update_row(i,inp[4])
            i += 1
            self.parameter_view.update_complex_row(i,inp[6])
            i += 1
            x = cart2pol(np.real(inp[6]),np.imag(inp[6]))
            self.parameter_view.update_polar_row(i,x[0],np.rad2deg(x[1]))
            i += 1
            self.parameter_view.update_row(i,np.abs(inp[7]))
            i += 1
            self.parameter_view.update_complex_row(i,inp[7])
            i += 1
            x = cart2pol(np.real(inp[7]),np.imag(inp[7]))
            self.parameter_view.update_polar_row(i,x[0],np.rad2deg(x[1]))
            i += 1
            self.parameter_view.update_row(i,np.abs(inp[8]))
            i += 1
            self.parameter_view.update_complex_row(i,inp[8])
            i += 1
            x = cart2pol(np.real(inp[8]),np.imag(inp[8]))
            self.parameter_view.update_polar_row(i,x[0],np.rad2deg(x[1]))
            i += 1
            self.parameter_view.update_complex_row(i,inp[10])

            self.U_phasor_graph.update("U_grid",inp[1],0)
            self.U_phasor_graph.update("U_load",x_Ur,y_Ur)
            self.U_phasor_graph.update("U_loss",x_Ur,y_Ur,x_r_loss,y_r_loss)
            self.U_phasor_graph.update("U_loss_r",x_U_rh,y_U_rh,inp[1],0)
            self.U_phasor_graph.update("U_loss_x",x_Ur,y_Ur,x_U_rh,y_U_rh)


            self.I_phasor_graph.update("I_system",np.real(inp[8]),np.imag(inp[8]))


        ### LAST LINE OF UPDATE METHOD, DO NOT EDIT OR ADD CODE AFTER
        self.graphing_flow_control()
        ### LAST LINE OF UPDATE METHOD, DO NOT EDIT OR ADD CODE AFTER
        # This allows simulator to progress to the next graphing step
