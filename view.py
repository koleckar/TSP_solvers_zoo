from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import (QRadioButton, QButtonGroup)

import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        width = 500
        height = 1200
        self.setGeometry(100, 100, width, height)
        self.setMaximumSize(height, width)
        self.setMinimumSize(height, width)
        self.setWindowTitle("EOA homework 1.")
        self.setWindowIcon(QtGui.QIcon("icons/icon.png"))

        layout2 = QtWidgets.QVBoxLayout()
        layout3 = QtWidgets.QVBoxLayout()

        self.plot1 = pg.PlotWidget()
        self.plot2 = pg.PlotWidget()
        self.plot1.setBackground('w')
        self.plot2.setBackground('w')
        self.plot1.setTitle("best solution")
        self.plot2.setTitle("stats over runs")
        self.plot1.hideAxis('bottom')
        self.plot1.hideAxis('left')
        self.plot2.setLabel('bottom', 'fitness evaluations')
        self.plot2.setLabel('left', 'fitness')
        self.plot2.showGrid(x=True, y=True)

        self.text_opt_gap = pg.TextItem("optimum gap=nan", color='r')
        self.plot2.addItem(self.text_opt_gap)
        self.text_fitness = pg.TextItem("fitness=nan", color='r')
        self.text_fitness.setPos(1, 1)
        self.plot1.addItem(self.text_fitness)

        self.plot1_lines = self.plot1.plot([], [], pen=pg.mkPen(width=1.5))
        self.plot2_lines = self.plot2.plot([], [], pen=pg.mkPen(width=2))

        layout2.addWidget(self.plot1)
        layout3.addWidget(self.plot2)

        layout_alg = QtWidgets.QHBoxLayout()
        # self.btn_ea = QRadioButton()
        # self.btn_ls = QRadioButton()
        # self.btn_ea.setText("ea")
        # self.btn_ls.setText("ls")
        #
        # bgp_algorithm = QButtonGroup()  # exclusive by default
        # bgp_algorithm.addButton(self.btn_ea, 0)
        # bgp_algorithm.addButton(self.btn_ls, 1)
        # layout_alg.addWidget(self.btn_ea)
        # layout_alg.addWidget(self.btn_ls)
        # layout_alg.addStretch(1)

        self.algorithms = QtWidgets.QComboBox()
        self.algorithms.addItems(["ea", "opt-2", "opt-3", "ls-custom"])
        layout_alg.addWidget(self.algorithms)

        self.initialization = QtWidgets.QComboBox()
        self.initialization.addItems(["random",
                                      "nearest_neighbor"])

        layout_params = QtWidgets.QFormLayout()
        self.runs = QtWidgets.QLineEdit()
        self.runs.setValidator(QtGui.QIntValidator())
        self.runs.setMaxLength(2)
        self.verbose = QtWidgets.QRadioButton()
        # self.plot_solutions = QtWidgets.QRadioButton()
        self.save_result_plot = QtWidgets.QRadioButton()
        self.save_result_file_name = QtWidgets.QLineEdit()
        self.save_result_file_name.setText("file_name")
        self.save_result_file_name.hide()
        self.verbose.setAutoExclusive(False)
        # self.plot_solutions.setAutoExclusive(False)
        self.save_result_plot.setAutoExclusive(False)
        self.dataset = QtWidgets.QComboBox()
        self.dataset.addItems(
            ["gr17.tsp", "gr21.tsp", "gr24.tsp", "gr48.tsp",
             "hk48.tsp",
             "si175.tsp", "si535.tsp", "si1032.tsp",
             "swiss42.tsp",
             "berlin52.tsp",
             "a280.tsp"])
        layout_params.addRow("dataset", self.dataset)
        layout_params.addRow("runs", self.runs)
        layout_params.addRow("initialization", self.initialization)
        layout_params.addRow("verbose", self.verbose)
        # layout_params.addRow("plot_solutions", self.plot_solutions)
        layout_params.addRow("save result plot", self.save_result_plot)
        layout_params.addRow("", self.save_result_file_name)

        specific_params = QtWidgets.QVBoxLayout()

        self.perturbation_operator = QtWidgets.QComboBox()
        self.perturbation_operator.addItems(["swap2",
                                             "reverse_sub"])

        self.ls_mode = QtWidgets.QComboBox()
        self.ls_mode.addItems(["first improving",
                               "best improving"])

        self.generations = QtWidgets.QLineEdit()
        self.population_size = QtWidgets.QLineEdit()
        self.parents_size = QtWidgets.QLineEdit()
        self.offspring_size = QtWidgets.QLineEdit()
        self.generations.setValidator(QtGui.QIntValidator())
        self.population_size.setValidator(QtGui.QIntValidator())
        self.offspring_size.setValidator(QtGui.QIntValidator())
        self.parents_size.setValidator(QtGui.QIntValidator())
        self.generations.setMaxLength(4)
        self.population_size.setMaxLength(4)
        self.offspring_size.setMaxLength(4)
        self.parents_size.setMaxLength(4)

        self.replacement_strategy = QtWidgets.QComboBox()
        self.replacement_strategy.addItems(["generational"])

        self.parent_selection = QtWidgets.QComboBox()
        self.parent_selection.addItems(["tournament"])

        self.crossover = QtWidgets.QComboBox()
        self.crossover.addItems(["pmx", "ox2", "erx"])

        self.mutation = QtWidgets.QComboBox()
        self.mutation.addItems(["swap2",
                                "reverse_sub"])

        self.mutation_prob = QtWidgets.QLineEdit()
        self.mutation_prob.setValidator(DoubleValidator())
        self.mutation_prob.setMaxLength(4)

        self.widget_specific_params_ea = QtWidgets.QWidget()
        self.widget_specific_params_ls = QtWidgets.QWidget()
        self.widget_specific_params_opt = QtWidgets.QWidget()
        specific_params_ea = QtWidgets.QFormLayout()
        specific_params_ls = QtWidgets.QFormLayout()
        specific_params_opt = QtWidgets.QFormLayout()

        specific_params_ls.addRow("perturbation", self.perturbation_operator)
        # specific_params_ls.addRow("ls_mode", self.ls_mode)

        specific_params_ea.addRow("generations", self.generations)
        specific_params_ea.addRow("population_size", self.population_size)
        specific_params_ea.addRow("offspring_size", self.offspring_size)
        specific_params_ea.addRow("parent_size", self.parents_size)
        specific_params_ea.addRow("replacement_strategy", self.replacement_strategy)
        specific_params_ea.addRow("parent_selection", self.parent_selection)
        specific_params_ea.addRow("crossover", self.crossover)
        specific_params_ea.addRow("mutation", self.mutation)
        specific_params_ea.addRow("mutation_prob", self.mutation_prob)

        self.widget_specific_params_ea.setLayout(specific_params_ea)
        self.widget_specific_params_ls.setLayout(specific_params_ls)
        self.widget_specific_params_opt.setLayout(specific_params_opt)

        self.widget_specific_params_ea.hide()
        self.widget_specific_params_ls.hide()
        self.widget_specific_params_opt.hide()
        specific_params.addWidget(self.widget_specific_params_ea)
        specific_params.addWidget(self.widget_specific_params_ls)
        specific_params.addWidget(self.widget_specific_params_opt)

        self.btn_start = QtWidgets.QPushButton()
        self.btn_start.setText("Start")
        self.btn_stop = QtWidgets.QPushButton()
        self.btn_stop.setText("Stop")

        layout1 = QtWidgets.QVBoxLayout()
        layout1.addLayout(layout_alg)
        layout1.addLayout(layout_params)
        layout1.addLayout(specific_params)
        layout1.addWidget(self.btn_start)
        layout1.addWidget(self.btn_stop)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addLayout(layout3)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()

    def instant_message(self, msg):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowIcon(QtGui.QIcon('icons/icon.png'))
        # msg_box.setIconPixmap(QtGui.QPixmap('icons/icon.xpm'))
        QtWidgets.QMessageBox.information(self, "info", msg)


class DoubleValidator(QtGui.QDoubleValidator):
    def __init__(self, *__args):
        super().__init__(*__args)

    def validate(self, p_str, p_int):

        if not p_str:
            return QtGui.QValidator.Intermediate, p_str, p_int

        if self.bottom() <= float(p_str) <= self.top():
            return QtGui.QValidator.Acceptable, p_str, p_int
        else:
            return QtGui.QValidator.Invalid, p_str, p_int
