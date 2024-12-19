'''SimuParameterWidget is used as the docking widget for setting simulation parameters'''


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
from decimal import Decimal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QGridLayout, QDoubleSpinBox,
                               QWidget, QLabel, QComboBox)
import UtilityFunctions as uFunc



class StartUp(QWidget):
    '''Placeholder widget for used during menu when there is no paramaters to edit'''
    def __init__(self, _):
        super().__init__()

        self.setMinimumWidth(240)
        self.setMaximumWidth(240)

        self.control_layout = QGridLayout()

        self.small_text = QLabel()
        self.small_text.setText("No open simulation,\nopen simulation to see parameters")
        self.control_layout.addWidget(self.small_text,0,0)
        self.big_label = QLabel()
        self.big_label.setText(" S \n I \n M \n U")
        os = uFunc.get_os()
        if os == "Linux":
            self.big_label.setStyleSheet("font-weight: bold; color: #333333")
        else:
            self.big_label.setStyleSheet("font-weight: bold; color: #adadad")
        self.big_label.setFont(QFont('Times', 100))
        self.control_layout.addWidget(self.big_label,1,0)

        self.setLayout(self.control_layout)



class SimuParameters(QWidget):
    '''Parameter edit docking widget used when simulation is open.\n
       Can handle numerical and dropdown menu inputs.\n
       For parameter symbol, character after underscore is subscripted.
       '''
    def __init__(self, parent, input_parameters):
        super().__init__()

        self.setMinimumWidth(200)
        self.setMaximumWidth(330)

        self.control_layout = QGridLayout()
        parent.simulation_control_signals.allow_full_parameter_edit.connect(self.allow_editing)

        self.name_labels = []       # Holds variable name Qlabels
        self.value_inputs = []      # Holds vairble input QDoubleSpinBoxes
        self.type_list = []         # Holds string vaibles of input types
        self.prefix_inputs = []     # Holds prefix selectors QSpinBox
        self.prefix_indexes = []    # Holds indexes of inputs with prefix selector  
        self.unit_labels = []       # Holds unit labels for inputs without prefixes QLabel
        self.editable_statuses = [] # Holds editability status True/False
        self.max_decimals = 3

        i_var = 0
        i_row = 0
        i_pref = 0
        i_dropdown = 0
        for key in input_parameters.keys():
            self.name_labels.append(QLabel())
            symbol = ""
            # symbol addition to name, subscripting of character after underscore
            if input_parameters[key]["symbol"] != "":
                symbol += "("
                char_list = list(input_parameters[key]["symbol"])
                for i, char in enumerate(char_list):
                    if i == 0:
                        symbol += char
                    else:
                        if char_list[i-1] == "_":
                            symbol += "<sub>"+ char + "</sub>"
                        elif char == "_":
                            symbol += ""
                        else:
                            symbol += char
            symbol += ")"

            self.name_labels[i_var].setText(input_parameters[key]["display_name"] + " " + symbol)

            self.control_layout.addWidget(self.name_labels[i_var],i_row,0,1,2)

            i_row += 1

            if input_parameters[key]["type"] == "number":
                self.type_list.append("number")
                self.value_inputs.append(QDoubleSpinBox())
                dec = Decimal(str(input_parameters[key]["init_value"]))
                dec = dec.as_tuple().exponent
                if dec > 0:
                    if input_parameters[key]["init_value"] > 1000:
                        self.value_inputs[i_var].setDecimals(0)
                    else:
                        self.value_inputs[i_var].setDecimals(2)
                else:
                    self.value_inputs[i_var].setDecimals(abs(dec)+1)
                if input_parameters[key]["maximum"] < input_parameters[key]["init_value"]:
                    self.value_inputs[i_var].setMaximum(input_parameters[key]["init_value"])
                else:   
                    self.value_inputs[i_var].setMaximum(input_parameters[key]["maximum"])
                if input_parameters[key]["init_value"] < input_parameters[key]["minimum"]:
                    self.value_inputs[i_var].setMinimum(input_parameters[key]["init_value"])
                else:
                    self.value_inputs[i_var].setMinimum(input_parameters[key]["minimum"])
                self.value_inputs[i_var].setValue(input_parameters[key]["init_value"])
                self.value_inputs[i_var].valueChanged.connect(lambda:self.input_value_changed(parent))
                self.control_layout.addWidget(self.value_inputs[i_var],i_row,0)
                self.value_inputs[i_var].setDisabled(True)
                if input_parameters[key]["editable"]:
                    self.value_inputs[i_var].setDisabled(False)
                    self.editable_statuses.append(True)
                else:
                    self.editable_statuses.append(False)

                prefixes = uFunc.unit_prefix(input_parameters[key]["unit"],
                                            input_parameters[key]["prefix_limits"][0],
                                            input_parameters[key]["prefix_limits"][1])
                if abs(min(input_parameters[key]["prefix_limits"])) > self.max_decimals:
                    self.max_decimals = abs(min(input_parameters[key]["prefix_limits"]))
                if len(prefixes) > 1:
                    self.prefix_inputs.append(QComboBox())
                    for pref in prefixes:
                        self.prefix_inputs[i_pref].addItem(pref)
                    current_pref = uFunc.unit_prefix(input_parameters[key]["unit"],
                                                    input_parameters[key]["default_prefix"],
                                                    input_parameters[key]["default_prefix"]
                                                    )
                    current_pref += input_parameters[key]["unit"]
                    current_pref_i = prefixes.index(current_pref[0])
                    self.prefix_inputs[i_pref].setCurrentIndex(current_pref_i)
                    self.prefix_indexes.append(i_var)
                    self.prefix_inputs[i_pref].setFixedWidth(65)
                    self.control_layout.addWidget(self.prefix_inputs[i_pref],i_row,1)
                    i_pref += 1
                else:
                    self.unit_labels.append(QLabel())
                    self.unit_labels[i_var-i_pref-i_dropdown].setText(input_parameters[key]["unit"])
                    self.control_layout.addWidget(self.unit_labels[i_var-i_pref-i_dropdown],i_row,1)

                i_row += 1
                i_var += 1

            elif input_parameters[key]["type"] == "dropdown":
                self.type_list.append("dropdown")
                self.value_inputs.append(QComboBox())
                for _,item in enumerate(input_parameters[key]["items"]):
                    self.value_inputs[i_var].addItem(item)
                    self.value_inputs[i_var].activated.connect(
                                                lambda:self.input_value_changed(parent))
                self.value_inputs[i_var].setEnabled(input_parameters[key]["editable"])
                self.editable_statuses.append(input_parameters[key]["editable"])
                self.control_layout.addWidget(self.value_inputs[i_var],i_row,0)

                i_row += 1
                i_var += 1
                i_dropdown += 1

        self.setLayout(self.control_layout)


    def input_value_changed(self, parent):
        '''Emits signal when parameter is changed'''
        parent.simulation_control_signals.update_inputs.emit(False)


    def allow_editing(self, inp):
        '''Changes the editable status of edvanced parameters'''
        for i,var in enumerate(self.value_inputs):
            if not self.editable_statuses[i]:
                var.setDisabled(inp)
