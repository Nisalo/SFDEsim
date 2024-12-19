"""Animated phasorgraph widget. Based on pyqtgraph."""


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
from PySide6.QtWidgets import QWidget, QGridLayout
import pyqtgraph as pg
import numpy as np


def linetype_maker(input_str):
    """Turn linetey string to linetype parameter list"""
    if input_str == "-":
        return [1, 1]
    if input_str == "..":
        return [1, 3]
    if input_str == "--":
        return [3, 1]


class PhasorGraphWidget(QWidget):
    """QWidget includind pg.plotwidget, setup for phasor diagrams"""
    num_outer_circle = 3
    bg_color = "#dedede"
    def __init__(self, name:str, x_name:str, y_name:str):
        super().__init__()
        print("PhasorPlotWidget init: " + name)
        self.graph_name = name
        self.x_name = x_name
        self.y_name = y_name

        self.frame_layout = QGridLayout()
        self.graphWidget = pg.PlotWidget()
        self.frame_layout.addWidget(self.graphWidget,0,0)
        self.phasors = {}

        self.num_of_bg_circles = 5
        self.current_V_max = ["",1]
        self.view_box_limits = 1
        self.txt_labels = []
        self.r_minmax = [0,0]

        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=False, y=False)
        self.graphWidget.setTitle(self.graph_name, color="b", size="20pt")
        styles = {"color": "red", "font-size": "18px"}
        self.graphWidget.setLabel("left", self.y_name, **styles)
        self.graphWidget.setLabel("bottom", self.x_name, **styles)
        self.y_limit = 1
        self.graphWidget.setYRange(-self.y_limit, self.y_limit)
        self.x_limit = 1
        self.graphWidget.setXRange(-self.x_limit, self.x_limit)
        self.graphWidget.setAspectLocked(lock=True, ratio=1)
        self.graphWidget.getPlotItem().hideAxis("bottom")
        self.graphWidget.getPlotItem().hideAxis("left")


        self.circle_list = []
        self.bg_pen = pg.mkPen(color=PhasorGraphWidget.bg_color)
        self.make_circular_bg(0.1, 0)
        self.horizontal_gline = self.graphWidget.plot([-1,1],[0,0], pen=self.bg_pen)
        self.vertical_gline = self.graphWidget.plot([0,0], [-1,1],pen=self.bg_pen)

        self.legend = pg.LegendItem()
        self.graphWidget.addItem(self.legend)

        self.setLayout(self.frame_layout)
        #self.setMaximumSize(100,100)


    def add_phasor(self, name, x_end, y_end, x_start=0, y_start=0, color="green"):
        """add new phasor with given arguments"""
        name = str(name)
        if name == self.phasors.keys():
            name = name + "_" + str(len(self.phasors))
        self.phasors[name] = Phasor(x_end, y_end, x_start, y_start, color)
        self.graphWidget.addItem(self.phasors[name])
        self.phasors[name].setZValue(100)
        phasor_end = round(np.sqrt((x_end**2 + y_end**2)),4)
        if phasor_end > self.current_V_max[1]:
            self.current_V_max[1] = phasor_end
            self.current_V_max[0] = name


    def update(self, name, x_end, y_end, x_start=0.0, y_start=0.0):
        """update phasor of given name to given coordinates"""
        #print("PPW update " + str(threading.get_ident()))
        name = str(name)
        self.phasors[name].phasor_update(x_start, x_end, y_start, y_end)
        new_V = round(np.sqrt((x_end**2 + y_end**2)),4)
        if new_V > self.current_V_max[1]:
            self.current_V_max[0] = name
            if new_V > self.current_V_max[1]*1.1:
                self.current_V_max[1] = new_V
                self.update_bg(new_V)
                Phasor.arrow_minimum = new_V*0.05
        elif name == self.current_V_max[0]:
            if new_V <= self.current_V_max[1]*0.9:
                self.current_V_max[1] = new_V
                self.update_bg(new_V)
                Phasor.arrow_minimum = new_V*0.05


    def update_bg(self, max_lenght):
        """Updates background grid based on maximum phsor lenght"""
        print("bg update")
        self.make_bg_lines(max_lenght)
        self.make_circular_bg(max_lenght, 1)
        self.graphWidget.setYRange(-self.view_box_limits, self.view_box_limits)
        self.graphWidget.setXRange(-self.view_box_limits, self.view_box_limits)
        self.graphWidget.setRange(xRange=[-self.view_box_limits, self.view_box_limits],
                                  yRange=[-self.view_box_limits, self.view_box_limits])
        gline_limits = self.graphWidget.getViewBox().viewRange()
        self.horizontal_gline.setData([gline_limits[0][0],gline_limits[0][1]], [0,0])
        self.vertical_gline.setData([0,0], [gline_limits[1][0],gline_limits[1][1]])


    def make_circular_bg(self, max_lenght, new_update):
        """Makes circular bg lines base on max lenght of phasor
        new_update == 0 when bg is new, else updates"""
        if max_lenght >= 5:
            max_lenght = np.ceil(max_lenght)
            while max_lenght % self.num_of_bg_circles != 0:
                max_lenght += 1
        elif max_lenght >= 1 and max_lenght < 5:
            max_lenght = np.ceil(max_lenght)
        else:
            div_num = 0
            while max_lenght < 1:
                div_num += 1
                max_lenght *= 10
            max_lenght = round(max_lenght+5,-1)/(10**div_num)
        self.view_box_limits = max_lenght
        r_list = []
        if new_update == 0:
            circle_spacing = max_lenght/self.num_of_bg_circles
            for r in list(np.linspace(circle_spacing,
                                      max_lenght + circle_spacing*PhasorGraphWidget.num_outer_circle,
                                      self.num_of_bg_circles+PhasorGraphWidget.num_outer_circle)):
                self.make_circle(r)
                r_list.append(r)
        else:
            i = 0
            circle_spacing = max_lenght/self.num_of_bg_circles
            for r in list(np.linspace(circle_spacing,
                                      max_lenght + circle_spacing*PhasorGraphWidget.num_outer_circle,
                                      self.num_of_bg_circles+PhasorGraphWidget.num_outer_circle)):
                self.update_circle(r,i)
                r_list.append(r)
                i += 2
        self.add_label_texts(r_list)
        self.r_minmax = [min(r_list),max(r_list)]


    def add_label_texts(self, r_list):
        """Adds radius marks to background"""
        for label in self.txt_labels:
            self.graphWidget.removeItem(label)
        self.txt_labels = []
        for i, r in enumerate(r_list):
            self.txt_labels.append(pg.TextItem(str(round(r,2)),
                                               anchor=(0.2,0)))
            self.graphWidget.addItem(self.txt_labels[i])
            self.txt_labels[i].setPos(r,0)


    def update_circle(self, r_max, circle_i):
        """Updates bg cirle based on radius and circle index"""
        x = list(np.linspace(-r_max,r_max,81))
        y = [np.sqrt(r_max**2 - xi**2) for xi in x]
        self.circle_list[circle_i].setData(x, y)
        y = [-yi for yi in y]
        self.circle_list[circle_i+1].setData(x, y)


    def make_circle(self, r_max):
        """creates bg circles based on radius"""
        x = list(np.linspace(-r_max,r_max,101))
        y = [np.sqrt(r_max**2 - xi**2) for xi in x]
        self.circle_list.append(self.graphWidget.plot(x, y, pen=self.bg_pen))
        y = [-yi for yi in y]
        self.circle_list.append(self.graphWidget.plot(x, y, pen=self.bg_pen))


    def make_bg_lines(self, max_lenght):
        """Makes horizontal and vertical bg lines"""
        self.horizontal_gline = self.graphWidget.plot([-max_lenght,max_lenght],[0,0], pen=self.bg_pen)
        self.vertical_gline = self.graphWidget.plot([0,0], [-max_lenght,max_lenght],pen=self.bg_pen)


    def remove_bg(self):
        """Removes background circles"""
        for circle in self.circle_list:
            self.graphWidget.removeItem(circle)


    def change_phasor_pen(self, name:str, color:str="", linetype:str="", width:int=""):
        """Change phasors drawing settings; color, linetype, width"""
        self.phasors[name].pen_change(color,linetype,width)


    def show_sector(self, sectors:list):
        """Select shown quadrant of the pahsorgraph, input as list of shown standard quadrant"""
        if len(sectors) == 1:
            if sectors[0] == 1:
                self.graphWidget.setYRange(-self.r_minmax[0], self.r_minmax[1])
                self.graphWidget.setXRange(-self.r_minmax[0], self.r_minmax[1])
            elif sectors[0] == 2:
                self.graphWidget.setYRange(-self.r_minmax[0], self.r_minmax[1])
                self.graphWidget.setXRange(-self.r_minmax[1], self.r_minmax[0])
            elif sectors[0] == 3:
                self.graphWidget.setYRange(-self.r_minmax[1], self.r_minmax[0])
                self.graphWidget.setXRange(-self.r_minmax[1], self.r_minmax[0])
            elif sectors[0] == 4:
                self.graphWidget.setYRange(-self.r_minmax[1], self.r_minmax[0])
                self.graphWidget.setXRange(-self.r_minmax[0], self.r_minmax[1])
        elif len(sectors) == 2:
            if min(sectors) == 1:
                if max(sectors) == 2:
                    self.graphWidget.setYRange(-self.r_minmax[0], self.r_minmax[1])
                    self.graphWidget.setXRange(-self.r_minmax[1], self.r_minmax[1])
                elif max(sectors) == 4:
                    self.graphWidget.setYRange(-self.r_minmax[1], self.r_minmax[1])
                    self.graphWidget.setXRange(-self.r_minmax[0], self.r_minmax[1])
            elif min(sectors) == 2:
                self.graphWidget.setYRange(-self.r_minmax[1], self.r_minmax[1])
                self.graphWidget.setXRange(-self.r_minmax[1], self.r_minmax[0])
            elif min(sectors) == 3:
                self.graphWidget.setYRange(self.r_minmax[0], -self.r_minmax[1])
                self.graphWidget.setXRange(-self.r_minmax[1], self.r_minmax[1])





class Phasor(pg.PlotCurveItem):
    """Phasor object for PhasorGraphWidget, based on pg.PlotCurveItem"""
    arrow_angle = np.pi/6
    arrow_multiplier = 0.1
    arrow_minimum = 0.05
    def __init__(self, x_end, y_end, x_start=0, y_star=0, color="green"):
        super().__init__()

        self.phasor_x_start = x_start
        self.phasor_y_start = y_star
        self.phasor_x_end = x_end
        self.phasor_y_end = y_end
        self.color = color
        self.linetype = "-"
        self.linewidth = 1

        x_len = self.phasor_x_end-self.phasor_x_start
        y_len = self.phasor_y_end-self.phasor_y_start
        self.arrow_len = Phasor.arrow_multiplier
        with np.errstate(divide='ignore', invalid='ignore'):
            self.phasor_angle = np.arctan((y_len)/(x_len))
        if x_end-x_start < 0:
            self.phasor_angle += np.pi

        self.pen = pg.mkPen(color=self.color, )
        self.setData(x=np.array([self.phasor_x_start, self.phasor_x_end,
                                 self.phasor_x_end - self.arrow_len * np.cos(self.phasor_angle+Phasor.arrow_angle),
                                 self.phasor_x_end,
                                 self.phasor_x_end - self.arrow_len * np.cos(self.phasor_angle-Phasor.arrow_angle)]),
                     y=np.array([self.phasor_y_start, self.phasor_y_end,
                                 self.phasor_y_end - self.arrow_len * np.sin(self.phasor_angle+Phasor.arrow_angle),
                                 self.phasor_y_end,
                                 self.phasor_y_end - self.arrow_len * np.sin(self.phasor_angle-Phasor.arrow_angle)]))
        self.setPen(self.pen)


    def phasor_update(self, new_x1, new_x2, new_y1, new_y2):
        """Updates phasor object based on new x and y values"""
        #print("phasor update")
        self.phasor_x_start = new_x1
        self.phasor_y_start = new_y1
        self.phasor_x_end = new_x2
        self.phasor_y_end = new_y2

        x_len = self.phasor_x_end-self.phasor_x_start
        y_len = self.phasor_y_end-self.phasor_y_start
        phasor_len = np.sqrt((x_len**2 + y_len**2))
        self.arrow_len = max(phasor_len * Phasor.arrow_multiplier, Phasor.arrow_minimum)
        with np.errstate(divide='ignore', invalid='ignore'):
            self.phasor_angle = np.arctan((y_len)/(x_len))
        if new_x2-new_x1 < 0:
            self.phasor_angle += np.pi

        self.setData(x=np.array([self.phasor_x_start, self.phasor_x_end,
                                 self.phasor_x_end - self.arrow_len * np.cos(self.phasor_angle+Phasor.arrow_angle),
                                 self.phasor_x_end,
                                 self.phasor_x_end - self.arrow_len * np.cos(self.phasor_angle-Phasor.arrow_angle)]),
                     y=np.array([self.phasor_y_start, self.phasor_y_end,
                                 self.phasor_y_end - self.arrow_len * np.sin(self.phasor_angle+Phasor.arrow_angle),
                                 self.phasor_y_end,
                                 self.phasor_y_end - self.arrow_len * np.sin(self.phasor_angle-Phasor.arrow_angle)]))


    def pen_change(self, color, linetype, width):
        """Change phasors drawing settings; color, linetype, width"""
        if color != "":
            self.color = color
        if linetype != "":
            self.linetype = linetype
        if width != "":
            self.linewidth = width
        dash = linetype_maker(self.linetype)
        self.pen = pg.mkPen(color=self.color,
                            width=self.linewidth,
                            dash = dash
                            )
        self.setPen(self.pen)
