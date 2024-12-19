"""Animated linegraph widget. Based on pyqtgraph. Includes buttons for x-axis zoom and
    toggling plotlines on and off."""

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
# pylint: disable=E1120
# pylint: disable=E1123
# pylint: disable=C0206
from copy import copy
from functools import partial
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
import pyqtgraph as pg
import numpy as np


def linetype_maker(input_str):
    """Turn linetype string to linetype parameter list"""
    if input_str == "-":
        return [1, 1]
    if input_str == "..":
        return [1, 3]
    if input_str == "--":
        return [2, 2]


def round_to(num, precision):
    """Round number to closest given precision value"""
    inver = precision**-1
    corr = 0.5 if num >= 0 else -0.5
    return round(int(num / precision+corr) * precision, int(np.log10(inver))-1)


class LinePlotWidget(QWidget):
    """QWidget including pg.plotwidget, setup for lineplots"""
    padding_factor = 0.005
    def __init__(self, name:str="Plot", x_name:str="x", y_name:str="y",
                 x_lenght:int=500, simu_steptime:float=0.001, plot_step:int=1,
                 enable_legend:bool=False):
        super().__init__()
        print("PhasorPlotWidget init: " + name)
        self.graph_name = name
        self.x_name = x_name
        self.y_name = y_name
        self.x_lenght = x_lenght
        self.steptime = simu_steptime
        self.step_len = plot_step

        self.widget_layout = QGridLayout()
        self.graphWidget = pg.PlotWidget()
        self.widget_layout.addWidget(self.graphWidget,0,0,1,4)
        self.plot_lines = {}
        self.click_markers = []
        self.click_text = []
        self.show_buttons = {}

        self.y_max = 0
        self.x_zoom_factor = 1
        self.x_min = x_lenght

        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setTitle(self.graph_name, color="b", size="20pt")
        styles = {"color": "red", "font-size": "18px"}
        self.graphWidget.setLabel("left", self.y_name, **styles)
        self.graphWidget.setLabel("bottom", self.x_name, **styles)
        self.graphWidget.setDefaultPadding(LinePlotWidget.padding_factor)
        self.graphWidget.scene().sigMouseClicked.connect(self.mouse_clicked)
        self.ref_y_limit(1)
        if enable_legend:
            self.graphWidget.addLegend()

        right_arrow = u'\U000021E4'
        left_arrow = u'\U000021E5'
        self.zoom_label = QLabel()
        self.zoom_label.setText("Zoom: ")
        self.x_zoom_in_button = QPushButton(" >in< ")
        self.x_zoom_in_button.clicked.connect(self.zoom_in_button_click)
        self.x_zoom_out_button = QPushButton(" <out> ")
        self.x_zoom_out_button.clicked.connect(self.zoom_out_button_click)
        self.x_zoom_out_button.setEnabled(False)
        self.show_label = QLabel()
        self.show_label.setText("Show: ")

        self.widget_layout.addWidget(self.zoom_label,1,0,1,1)
        self.widget_layout.addWidget(self.x_zoom_in_button,1,1,1,1)
        self.widget_layout.addWidget(self.x_zoom_out_button,1,2,1,1)
        self.widget_layout.addWidget(self.show_label,1,3,1,1)

        #self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.setLayout(self.widget_layout)


    def add_plot_show_buttons(self, name:str):
        '''Creates the buttons for toggling plotline visibility ON/OFF'''
        cols = self.widget_layout.columnCount()
        i = len(list(self.plot_lines.keys()))-1
        self.show_buttons[name] = QPushButton(name, self)
        self.show_buttons[name].clicked.connect(partial(self.show_button_clicked, name=name))
        self.show_buttons[name].setCheckable(True)
        self.show_buttons[name].setChecked(True)
        self.widget_layout.addWidget(self.show_buttons[name],1,cols+i,1,1)
        self.widget_layout.addWidget(self.graphWidget,0,0,1,cols+i+10)


    def show_button_clicked(self, name:int):
        '''Toggles plotline visibility ON/OFF'''
        self.plot_lines[name].setVisible(self.show_buttons[name].isChecked())


    def add_plotline(self, name, x_data, y_data, color="red"):
        """Add a new line plot, with given inputs and self.parameters"""
        name = str(name)
        if name == self.plot_lines.keys():
            name = name + "_" + str(len(self.plot_lines))
        if len(x_data) < self.x_lenght:
            base_500 = np.arange((-self.x_lenght)+1,1,1)
            x_data = copy(base_500)
        if len(y_data) < self.x_lenght:
            base_500 = np.zeros(self.x_lenght)
            for i, num in enumerate(y_data):
                ind = abs(int(x_data[i]))
                base_500 = np.delete(base_500,ind)
                base_500 = np.insert(base_500,ind,num)
            y_data = copy(base_500)
        if len(x_data) > self.x_lenght or len(y_data) > self.x_lenght:
            x_data = x_data[len(x_data)-self.x_lenght:len(x_data)]
            y_data = y_data[len(x_data)-self.x_lenght:len(x_data)]
        x_data = x_data * self.steptime * self.step_len
        self.plot_lines[name] = PlotLine(name, x_data, y_data, color)
        self.graphWidget.addItem(self.plot_lines[name])
        self.ref_y_limit(max([abs(min(y_data)),abs(max(y_data))]))

        self.add_plot_show_buttons(name)


    def update(self, name, x_data_new, y_data_new):
        """Update lineplot with given inputs, replaces the current plot"""
        self.plot_lines[str(name)].plotline_update(x_data_new, y_data_new)
        self.ref_y_limit(max([min(y_data_new),max(y_data_new)]))


    def step(self, name, y_new):
        """Add new step to the lineplot, y-value is given, rest from self.parameters"""
        self.plot_lines[str(name)].plotline_step( y_new, self.step_len*self.steptime)
        self.ref_y_limit(max([abs(y_new),y_new]))
        self.update_x_range()


    def ref_y_limit(self,y_limit):
        """Calculates and sets the y-limits"""
        if y_limit > self.y_max:
            self.graphWidget.setYRange(-y_limit, y_limit)
            self.y_max = y_limit


    def set_text(self, title:str="", y_label:str="", x_label:str="",
                 title_color:str="b", label_color:str="r",
                 title_size:int=20, axis_size:int=18):
        """Set graph title and axis text, color and font-size"""
        if title != "":
            self.graph_name = title
        if y_label != "":
            self.y_name = y_label
        if x_label != "":
            self.x_name = x_label
        self.graphWidget.setTitle(self.graph_name, color=title_color, size=str(title_size)+"pt")
        styles = {"color": label_color, "font-size": str(axis_size)+"px"}
        self.graphWidget.setLabel("left", self.y_name, **styles)
        self.graphWidget.setLabel("bottom", self.x_name, **styles)


    def change_line_pen(self, name:str, color:str="", linetype:str="", width:int=""):
        """Change lineplot color, linetype and width"""
        self.plot_lines[name].pen_change(color,linetype,width)


    def update_x_range(self):
        """x-axis panning"""
        minmax = self.plot_lines[list(self.plot_lines.keys())[0]].get_x_minmax(self.x_lenght,
                                                                               self.x_min)
        self.graphWidget.setXRange(minmax[0],minmax[1])


    def zoom_in_button_click(self):
        """Set x-axis for zoom in"""
        self.x_zoom_factor *= 0.9
        self.x_min = self.x_zoom_factor*self.x_lenght
        self.update_x_range()
        if self.x_zoom_factor >= 0.9:
            self.x_zoom_out_button.setEnabled(True)


    def zoom_out_button_click(self):
        """Set x-axis for zoom out"""
        self.x_zoom_factor /= 0.9
        if round(self.x_zoom_factor,1) > 1:
            self.x_zoom_factor *= 0.9
        self.x_min = self.x_zoom_factor*self.x_lenght
        self.update_x_range()
        if self.x_zoom_factor >= 1:
            self.x_zoom_out_button.setEnabled(False)


    def mouse_clicked(self, click_event):
        """Left click action in graph"""
        if click_event.button() != Qt.MouseButton.LeftButton:
            return
        lookup_range = 1
        vb = self.graphWidget.plotItem.vb
        scene_coords = click_event.scenePos()
        if self.graphWidget.sceneBoundingRect().contains(scene_coords):
            mouse_point = vb.mapSceneToView(scene_coords)
            print(f'clicked plot X: {mouse_point.x()}, Y: {mouse_point.y()}, event: {click_event}')
        closest = round_to(mouse_point.x(), self.steptime)
        i_round = int(np.log10(self.steptime**-1))-1
        x_index = self.plot_lines[list(self.plot_lines.keys())[0]].get_i_of_x(closest,i_round)
        if x_index < 0:
            return
        key_index = 0
        abs_distances = []
        xy_coordinates = []
        for key in self.plot_lines.keys():
            abs_distances.append([])
            xy_coordinates.append([])
            for x_index_i in range(x_index-lookup_range,x_index+lookup_range):
                if x_index_i > self.x_lenght-1:
                    break
                if x_index_i < 0:
                    break
                y_val = self.plot_lines[key].get_y_at_i(x_index_i)
                x_val = self.plot_lines[key].get_x_at_i(x_index_i)
                abs_distances[key_index].append(np.sqrt((mouse_point.x()-x_val)**2 + (mouse_point.y()-y_val)**2))
                xy_coordinates[key_index].append([x_val, y_val])
            key_index += 1
        min_line = min(range(len(abs_distances)), key=abs_distances.__getitem__)
        point_min_ind = min(range(len(abs_distances[min_line])),
                            key=abs_distances[min_line].__getitem__)
        xy = [xy_coordinates[min_line][point_min_ind][0],
              xy_coordinates[min_line][point_min_ind][1]]
        color = str(self.plot_lines[list(self.plot_lines.keys())[min_line]].color)
        self.click_markers.append(pg.ArrowItem(pen={"color": color}, brush=color))
        self.click_markers[len(self.click_markers)-1].setPos(xy[0],xy[1])
        self.graphWidget.addItem(self.click_markers[len(self.click_markers)-1])
        text = "x:"+ str(round_to(xy[0],self.steptime)) +"\ny:"+ str(round_to(xy[1],self.steptime))
        self.click_text.append(pg.TextItem(text=text))
        self.click_text[len(self.click_text)-1].setPos(xy[0],xy[1])
        self.graphWidget.addItem(self.click_text[len(self.click_text)-1])



class PlotLine(pg.PlotCurveItem):
    """Lineplot object for LinePlotWidget, based on pg.PlotCurveItem"""
    def __init__(self, name, x_data, y_data, color="red"):
        super().__init__()
        print("PlotLine init: " + name)

        self.x_data = x_data
        self.y_data = y_data
        self.color = color
        self.linetype = "-"
        self.linewidth = 1

        self.pen = pg.mkPen(color=self.color)
        self.setData(self.x_data, self.y_data, pen=self.pen, name=name)


    def plotline_step(self, y_new, step):
        """Add new step to plotline"""
        self.x_data = np.delete(self.x_data,0)
        self.x_data = np.append(self.x_data,self.x_data[-1]+step)
        self.y_data = np.delete(self.y_data,0)
        self.y_data = np.append(self.y_data,y_new)
        self.setData(self.x_data, self.y_data)


    def plotline_update(self, x_data, y_data):
        """Update the complete plotline data"""
        self.setData(x_data, y_data)


    def pen_change(self, color, linetype, width):
        """Change pen settings of the lineplot"""
        if color != "":
            self.color = color
        if linetype != "":
            self.linetype = linetype
        if width != "":
            self.linewidth = width
        dash = linetype_maker(self.linetype)
        self.pen = pg.mkPen(color=self.color,
                            width=self.linewidth,
                            dash=dash)
        self.setPen(self.pen)


    def get_y_at_i(self,i):
        """Return y-axis value at given index"""
        return float(self.y_data[i])


    def get_x_at_i(self,i):
        """Return x-axis value at given index"""
        return float(self.x_data[i])


    def get_i_of_x(self, x, i_round):
        """Return index of x-axis value, with given rounding"""
        try:
            return np.where(np.round(self.x_data,i_round)==x)[0][0]
        except IndexError:
            return -1


    def get_x_minmax(self, lenght, limit):
        """Return x values for panning"""
        return [self.x_data[int(lenght-limit)], self.x_data[-1]]
