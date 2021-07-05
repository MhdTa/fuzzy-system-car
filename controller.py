from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout,
                             QGroupBox, QPushButton, QComboBox, QStackedWidget,
                             QFormLayout, QLabel, QSlider, QDoubleSpinBox, QFileDialog)
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from os.path import join

from simulator import Run
from fuzzy_system import MyFuzzy_system


class Information_frame(QFrame):
    def __init__(self, display):
        super().__init__()
        self.display_frame = display
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.load_data()
        self.thread_running = False
        self.running_option()
        # self.variable_setting()
        self.monitor_setting()

    def running_option(self):
        group = QGroupBox("Run")
        group_layout = QHBoxLayout()
        group.setLayout(group_layout)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.start_simulation)
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setDisabled(True)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setDisabled(True)

        group_layout.addWidget(self.run_btn)
        group_layout.addWidget(self.pause_btn)
        group_layout.addWidget(self.stop_btn)
        self.layout.addWidget(group)

    def monitor_setting(self):
        group = QGroupBox("Simulation imformation")
        group_layout = QFormLayout()

        self.l_car_pos = QLabel("0 , 0")
        self.l_front_dist = QLabel("0.0")
        self.label_l_dist = QLabel("0.0")
        self.label_r_dist = QLabel("0.0")
        self.l_car_angle = QLabel("0.0")
        self.l_wheel_angle = QLabel("0.0")
        group_layout.addRow(QLabel("Car position :"), self.l_car_pos)
        group_layout.addRow(QLabel("Car angle :"), self.l_car_angle)
        group_layout.addRow(QLabel("Front distance :"), self.l_front_dist)
        group_layout.addRow(QLabel("Left side distance :"), self.label_l_dist)
        group_layout.addRow(QLabel("Right side distance :"), self.label_r_dist)
        group_layout.addRow(QLabel("Wheel angle :"), self.l_wheel_angle)

        group.setLayout(group_layout)
        self.layout.addWidget(group)

    @pyqtSlot()
    def start_simulation(self):
        self.system = MyFuzzy_system()
        self.simulator_thread = Run(self.system, self.dataset)
        self.simulator_thread.started.connect(self.__init_controller)
        self.simulator_thread.finished.connect(self.__reset_controller)
        self.simulator_thread.sig_connect(p_init=self.display_frame.init_walls,
                                          p_car=self.move_car,
                                          collide=self.display_frame.collide,
                                          log=self.simulation_log)

        self.thread_running = True
        self.simulator_thread.start()

    @pyqtSlot()
    def __init_controller(self):
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.run_btn.setDisabled(True)

        self.pause_btn.clicked.connect(self.simulator_thread.paused)
        self.stop_btn.clicked.connect(self.simulator_thread.stop)

    @pyqtSlot()
    def __reset_controller(self):
        self.pause_btn.setDisabled(True)
        self.stop_btn.setDisabled(True)
        self.run_btn.setEnabled(True)
        self.thread_running = False

    @pyqtSlot(list, list, list, float)
    def move_car(self, pos_angle, inters, dists, wheel_ouput):
        self.l_car_pos.setText("{:.3f},{:.3f}".format(*pos_angle[:2]))
        self.l_car_angle.setText(str(pos_angle[2]))
        self.l_front_dist.setText(str(dists[0]))
        self.label_l_dist.setText(str(dists[1]))
        self.label_r_dist.setText(str(dists[2]))
        self.l_wheel_angle.setText(str(wheel_ouput))

        self.display_frame.update_car(pos_angle, inters)

    @pyqtSlot(dict)
    def simulation_log(self, log):

        self.log = log
        self.display_frame.show_path(self.log['x'], self.log['y'])

    @pyqtSlot()
    def save_data(self):
        save_dir = QFileDialog.getExistingDirectory(self, 'Save As')
        path_4d = join(save_dir, 'train4D.txt')
        path_6d = join(save_dir, 'train6D.txt')
        data_lines = list(zip(*self.log.values()))
        with open(path_6d, 'w') as f6d:
            for line in data_lines:
                f6d.write("{:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f}\n".format(
                    line[0], line[1], line[2], line[3], line[4], line[5]))

        with open(path_4d, 'w') as f4d:
            for l in data_lines:
                f4d.write("{:.3f} {:.3f} {:.3f} {:.3f}\n".format(
                    l[2], l[3], l[4], l[5]))

    def load_data(self, path='./data/case01.txt'):
        data = []
        with open(path, 'r', encoding='utf8') as f:
            for line in f:
                data.append(tuple(line.strip().split(',')))
        self.dataset = {
            "start_pos": data[0][:2],
            "start_wheel_angle": data[0][2],
            "finishline_l": data[1],
            "finishline_r": data[2],
            "walls": data[3:]
        }
    # def load_path


class Variable_setting_frame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel | QFrame.Plain)
        layout = QFormLayout()
        self.setLayout(layout)
