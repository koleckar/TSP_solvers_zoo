from PyQt5.QtCore import QThread, QTimer, QEventLoop, pyqtSignal
from view import MainWindow
from plotting_pyqtgraph import plot_solution, plot_graph_nodes, plot_fitness_graph
import function_tools
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters


# todo:
#   5. 2-opt, 3-opt - There might be invalid opt allowed ??
#   6. ls: best-improving, first-improving
#   -. ea: add NN init method
#   7. learn how to make .exe
#   8. run all test
#   9. make short report
#   -. threads not synchronised, plot save must be done after ViewUpdaters work
#   -. add progress bar
#   -. reset values after end of the run and search-kill(stop btn) correctly
#   3. plot line ending prematurely
#   12. plots visuals not consistent, best sol. ends sooner, and opt gap in stats over run dont match line end point
#   10. optimum gap not visible
#   11. dataset name to plots?
# todo done:
#   1. save results plot controller param, save both images
#   2. plot_solutions radiobutton now does nothing
#   4. local search same api as ea

class Controller:

    # Forward references: (To remove circular dependency, import only for annotating Type):
    #   "When a type hint contains names that have not been defined yet,
    #   that definition may be expressed as a string literal, to be resolved later."
    def __init__(self, view: 'MainWindow', model: 'Model'):
        self.view = view

        self.model = model

        self.worker = WorkerThread(self)

        # todo: add refresh time param for view_updater
        self.view_updater_refresh_time = 150  # ms
        self.view_updater = ViewUpdater(self)

        self.default_widget_values()

        self.connect_widgets_to_slots()

        self.default_plots()

        # self.worker.finished.connect(self.worker_finished)
        self.view_updater.view_updater_done.connect(self.run_finished)

    def default_plots(self):
        plot_graph_nodes(self.model, self.view.plot1)
        k = self.model.params_general["solution_size"]
        plot_solution(self.model, [0] * k, np.nan, self.view.plot1, self.view.plot1_lines)

        self.view.plot2.addItem(pg.InfiniteLine(self.model.params_general["optimum"], angle=0,
                                                pen=pg.mkPen(width=1, color='g')), label="optimum")

    def default_widget_values(self):
        self.view.dataset.setCurrentText(self.model.params_general["dataset_name"])
        self.view.runs.setText(str(self.model.params_general["runs"]))
        self.view.generations.setText(str(self.model.params_general["generations"]))
        self.view.population_size.setText(str(self.model.params_ea["population_size"]))
        self.view.offspring_size.setText(str(self.model.params_ea["offspring_size"]))
        self.view.parents_size.setText(str(self.model.params_ea["parents_size"]))
        self.view.mutation_prob.setText(str(self.model.params_ea["mutation_prob"]))
        if self.model.params_general["save_result_plot"]:
            self.view.save_result_plot.setChecked(True)
            self.view.save_result_file_name.setText(self.model.params_general["save_results_file_name"])
            self.view.save_result_file_name.show()

        if self.model.params_general["verbose"]:
            self.view.verbose.setChecked(True)
        self.view.btn_stop.setEnabled(False)

        if self.model.algorithm_name == "ea":
            self.view.widget_specific_params_ea.show()
        if self.model.algorithm_name == "ls":
            self.view.widget_specific_params_ls.show()
        if self.model.algorithm_name == "opt-2" or self.model.algorithm_name == "opt-3":
            self.view.widget_specific_params_opt.show()

    def connect_widgets_to_slots(self):
        # self.view.btn_ea.clicked.connect(self.update_algorithm)
        # self.view.btn_ls.clicked.connect(self.update_algorithm)
        self.view.algorithms.activated.connect(self.update_algorithm)

        self.view.dataset.activated.connect(self.update_dataset)

        self.view.runs.textChanged.connect(self.update_general_params)
        self.view.verbose.clicked.connect(self.update_general_params)
        # self.view.plot_solutions.clicked.connect(self.update_general_params)
        self.view.save_result_plot.clicked.connect(self.update_general_params)
        self.view.save_result_file_name.textChanged.connect(self.update_general_params)

        self.view.perturbation_operator.activated.connect(self.update_ls_params)
        self.view.ls_mode.activated.connect(self.update_general_params)
        self.view.initialization.activated.connect(self.update_general_params)

        self.view.generations.textChanged.connect(self.update_ea_params)
        self.view.population_size.textChanged.connect(self.update_ea_params)
        self.view.offspring_size.textChanged.connect(self.update_ea_params)
        self.view.parents_size.textChanged.connect(self.update_ea_params)
        self.view.parent_selection.activated.connect(self.update_ea_params)
        self.view.crossover.activated.connect(self.update_ea_params)
        self.view.mutation.activated.connect(self.update_ea_params)
        self.view.mutation_prob.textChanged.connect(self.update_ea_params)
        self.view.replacement_strategy.activated.connect(self.update_ea_params)

        self.view.btn_start.clicked.connect(self.start_app)
        self.view.btn_stop.clicked.connect(self.kill_app)

    def update_algorithm(self):
        alg = self.view.algorithms.currentText()

        if alg == "ea":
            self.view.widget_specific_params_ea.show()
            self.view.widget_specific_params_ls.hide()
            self.model.algorithm_name = "ea"

        if alg == "ls-custom":
            self.view.widget_specific_params_ea.hide()
            self.view.widget_specific_params_ls.show()
            self.model.algorithm_name = "ls"

        if alg == "opt-2":
            self.view.widget_specific_params_ea.hide()
            self.view.widget_specific_params_ls.hide()
            self.view.widget_specific_params_opt.show()
            self.model.algorithm_name = "opt-2"

        if alg == "opt-3":
            self.view.widget_specific_params_ea.hide()
            self.view.widget_specific_params_ls.hide()
            self.view.widget_specific_params_opt.show()
            self.model.algorithm_name = "opt-3"

        self.model.params_general['algorithm'] = self.model.available_algorithms[self.model.algorithm_name]
        self.model.params_general["save_results_file_name"] = self.model.dataset_name + "_" + self.model.algorithm_name
        self.view.save_result_file_name.setText(self.model.params_general["save_results_file_name"])

        print(self.model.params_general) if self.model.params_general["verbose"] else ...

    def update_dataset(self):
        self.view.instant_message("Loading dataset.") if self.model.params_general["verbose"] else ...
        self.model.dataset_name = self.view.dataset.currentText()
        self.model.update_chosen_dataset()

        self.view.plot1.clear()
        self.view.plot1_lines = self.view.plot1.plot([0], [0])
        plot_graph_nodes(self.model, self.view.plot1)
        k = self.model.params_general["solution_size"]
        plot_solution(self.model, [0] * k, np.nan, self.view.plot1, self.view.plot1_lines)

        self.view.plot2.clear()
        self.view.plot2.addItem(pg.InfiniteLine(self.model.params_general["optimum"], angle=0,
                                                pen=pg.mkPen(width=1, color='g')), label="optimum")

        print(self.model.params_general) if self.model.params_general["verbose"] else ...

    def update_general_params(self):
        if self.view.verbose.isChecked():
            self.model.params_general["verbose"] = True
        else:
            self.model.params_general["verbose"] = False

        # if self.view.plot_solutions.isChecked():
        #     self.model.params_general["plot_solutions"] = True
        # else:
        #     self.model.params_general["plot_solutions"] = False

        if self.view.save_result_plot.isChecked():
            self.model.params_general["save_result_plot"] = True
            self.view.save_result_file_name.show()
            self.model.params_general["save_results_file_name"] = self.view.save_result_file_name.text()
        else:
            self.model.params_general["save_result_plot"] = False
            self.view.save_result_file_name.hide()

        # todo: do some validity checking, add timer for user input.
        try:
            runs = int(self.view.runs.text())
        except ValueError:
            return
        self.model.params_general["runs"] = runs

        print(self.model.params_general) if self.model.params_general["verbose"] else ...

    def update_ls_params(self):
        alg_text = self.view.perturbation.currentText()
        if alg_text is "opt-2-best-improving":
            ...
            # self.model.
            #
            # self.perturbation_operator.addItems(["opt-2-best-improving",
            #                                      "opt-3-best-improving",
            #                                      "swap2",
            #                                      "reverse_sub"])
            # "ls": local_search,
            # "opt-2": opt_2_best_improving,
            # "opt-3": opt_3_best_improving
        # self.view.ls_mode.clicked.currentText()
        # self.view.initialization.currentText()

    def update_ea_params(self):
        try:
            generations = int(self.view.generations.text())
            population_size = int(self.view.population_size.text())
            parents_size = int(self.view.parents_size.text())
            offspring_size = int(self.view.offspring_size.text())
            mutation_prob = float(self.view.mutation_prob.text())
        except ValueError:
            return

        self.model.params_ea["generations"] = generations

        self.model.params_ea["population_size"] = population_size

        self.model.params_ea["parents_size"] = parents_size

        self.model.params_ea["offspring_size"] = offspring_size

        self.model.params_ea["parent_selection"] = self.view.parent_selection.currentText()
        self.model.params_ea["replacement_strategy"] = self.view.replacement_strategy.currentText()
        self.model.params_ea["crossover"] = self.view.crossover.currentText()
        self.model.params_ea["mutation"] = self.view.mutation.currentText()

        self.model.params_ea["mutation_prob"] = mutation_prob

        print(self.model.params_ea)

    def model_stats_reset(self):
        self.model.stats_over_runs = []
        self.model.stats = []
        self.model.actual_run = 0
        self.model.bsf = [np.nan, np.nan]

    def set_enabled_widgets(self, b):
        self.view.btn_start.setEnabled(b)
        # self.view.btn_ea.setEnabled(b)
        # self.view.btn_ls.setEnabled(b)
        # self.view.plot_solutions.setEnabled(b)
        self.view.initialization.setEnabled(b)
        self.view.save_result_plot.setEnabled(b)
        self.view.save_result_file_name.setEnabled(b)
        self.view.dataset.setEnabled(b)
        self.view.runs.setEnabled(b)
        self.view.generations.setEnabled(b)

        self.view.population_size.setEnabled(b)
        self.view.offspring_size.setEnabled(b)
        self.view.parents_size.setEnabled(b)
        self.view.parent_selection.setEnabled(b)
        self.view.crossover.setEnabled(b)
        self.view.mutation.setEnabled(b)
        self.view.mutation_prob.setEnabled(b)
        self.view.replacement_strategy.setEnabled(b)

        self.view.perturbation_operator.setEnabled(b)
        self.view.ls_mode.setEnabled(b)

    # todo: wait few seconds after user input the mutation prob, than notify it's not correct
    def params_valid(self):
        # if not self.view.btn_ls.isChecked() and not self.view.btn_ea.isChecked():
        #     self.view.instant_message("Please choose algorithm.")
        #     return False

        if self.model.algorithm_name == "ea":
            try:
                generations = int(self.view.generations.text())
            except ValueError:
                self.view.instant_message("Invalid generations size!")
                return False
            try:
                population_size = int(self.view.population_size.text())
            except ValueError:
                self.view.instant_message("Invalid population_size!")
                return False
            try:
                parents_size = int(self.view.parents_size.text())
            except ValueError:
                self.view.instant_message("Invalid parents_size!")
                return False
            try:
                offspring_size = int(self.view.offspring_size.text())
            except ValueError:
                self.view.instant_message("Invalid offspring_size!")
                return False

            if generations <= 0:
                self.view.instant_message("generations must be > 0")
                return False
            if population_size <= 0:
                self.view.instant_message("population_size must be > 0")
                return False
            if parents_size <= 0:
                self.view.instant_message("parents_size must be > 0")
                return False
            if offspring_size <= 0:
                self.view.instant_message("offspring_size must be > 0")
                return False

        return True

    def start_app(self):
        if not self.params_valid():
            return

        self.set_enabled_widgets(False)
        self.view.btn_stop.setEnabled(True)

        self.view_updater.start()

        self.worker.start()

    def run_finished(self, is_done):
        print("best fitness end:" + str(self.model.bsf[1]) + " i:" + str(self.view_updater.i) + "len:" + str(
            len(self.model.stats_over_runs[0]["stats"])))

        self.view.instant_message("Search done!")
        self.set_enabled_widgets(True)
        if self.view.save_result_plot.isChecked():
            exporter = pg.exporters.ImageExporter(self.view.plot1.plotItem)
        exporter.export(self.model.params_general["save_results_file_name"] + "_best_solution.png")
        exporter = pg.exporters.ImageExporter(self.view.plot2.plotItem)
        exporter.export(self.model.params_general["save_results_file_name"] + "_stats_over_runs.png")

        self.model_stats_reset()

    def worker_finished(self):
        print("best fitness end:" + str(self.model.bsf[1]) + " i:" + str(self.view_updater.i) + "len:" + str(
            len(self.model.stats_over_runs[0]["stats"])))

        self.view.instant_message("Search done!")
        self.set_enabled_widgets(True)
        if self.view.save_result_plot.isChecked():
            exporter = pg.exporters.ImageExporter(self.view.plot1.plotItem)
        exporter.export(self.model.params_general["save_results_file_name"] + "_best_solution.png")
        exporter = pg.exporters.ImageExporter(self.view.plot2.plotItem)
        exporter.export(self.model.params_general["save_results_file_name"] + "_stats_over_runs.png")

    # todo: or set model.iterate to false?
    # todo: reset model stats after stop!
    def kill_app(self):
        self.worker.exit()
        self.view_updater.exit()
        self.set_enabled_widgets(True)
        self.view.instant_message("Search killed!")
        self.view.btn_stop.setEnabled(False)
        self.model_stats_reset()
        self.blank_plots()

    def blank_plots(self):
        ...


# todo: would be better to have each run as separate function, so you can emmit a signal each time...
# this way, if somehow view_updater was faster than worker, the data in
class ViewUpdater(QThread):
    view_updater_done = pyqtSignal(bool)

    def worker_finished_signal(self):
        self.worker_finished = True

    def __init__(self, controller, *args, **kwargs):
        QThread.__init__(self, *args, **kwargs)
        self.controller = controller

        self.timer = QTimer()
        self.timer.moveToThread(self)
        self.timer.setInterval(controller.view_updater_refresh_time)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.update_view_plots)
        self.stats_len = len(self.controller.model.stats)
        self.i = 0
        self.actual_run = 0
        self.worker_finished = False
        self.this_run_plotted = False
        self.controller.worker.finished.connect(self.worker_finished_signal)

    # todo: mutex for stats?
    # todo: multiple runs
    def update_view_plots(self):

        if self.this_run_plotted:
            if self.worker_finished and self.actual_run == self.controller.model.actual_run:
                self.worker_finished = False
                self.this_run_plotted = True
                self.view_updater_done.emit(True)

                self.timer.stop()
                self.timer.timeout.disconnect(self.update_view_plots)
                self.loop.exit()
                self.exit()

            self.actual_run = np.minimum(self.actual_run + 1, self.controller.model.actual_run)
            self.i = 0
            self.this_run_plotted = False

        stats = self.controller.model.stats_over_runs[self.controller.model.actual_run]["stats"]
        self.stats_len = len(stats)

        if self.i >= self.stats_len:
            if self.actual_run < self.controller.model.actual_run:
                self.this_run_plotted = True
                return

            if self.worker_finished:
                self.worker_finished = False
                self.this_run_plotted = True
                self.view_updater_done.emit(True)
                self.timer.stop()
                self.timer.timeout.disconnect(self.update_view_plots)
                self.loop.exit()
                self.exit()
            return

        bsf_solution = stats[self.i][0]
        bsf_fitness = stats[self.i][1]
        if bsf_solution is np.nan:
            return

        self.controller.view.text_fitness.setText('fitness=' + str(bsf_fitness))
        plot_solution(self.controller.model, bsf_solution, bsf_fitness,
                      self.controller.view.plot1, self.controller.view.plot1_lines)

        if self.i >= 1:
            plot_fitness_graph(self.controller.model, stats[0:self.i], self.controller.view.plot2_lines)

            opt = self.controller.model.params_general["optimum"]
            opt_gap = np.round(np.abs(bsf_fitness - opt) / opt * 100, 2)
            self.controller.view.text_opt_gap.setText("opt_gap=" + str(opt_gap) + "%, ")
        else:
            print("plot2 reset")
            self.controller.view.plot2_lines = self.controller.view.plot2.plot([bsf_fitness], [0],
                                                                               pen=pg.mkPen(width=1, color='b'))
        self.i += 1

    def run(self):
        self.timer.start(self.controller.view_updater_refresh_time)
        self.loop = QEventLoop()
        self.loop.exec_()


# todo: signal worker - computing done -> registered by view_updater to know if i >= len.stats
# THE PROBLEM WAS THAT STATS WERE FLUSHED !  => HAVE ONE STRUCTURE STATS OVER RUNS
#
class WorkerThread(QThread):
    work_done = pyqtSignal(bool)

    def __init__(self, controller, parent=None, index=0):
        super(WorkerThread, self).__init__(parent)
        self.controller = controller
        self.index = index

    def run(self):
        print("WorkerThread starting...")
        function_tools.collect_statistics(self.controller.model)
        print("WorkerThread finished.")

    # def update_algorithm(self):
    #
    #     if self.view.btn_ea.isChecked():
    #         self.view.widget_specific_params_ea.show()
    #         self.view.widget_specific_params_ls.hide()
    #         self.model.algorithm_name = "ea"
    #
    #     if self.view.btn_ls.isChecked():
    #         self.view.widget_specific_params_ea.hide()
    #         self.view.widget_specific_params_ls.show()
    #         self.model.algorithm_name = "ls"
    #
    #     self.model.params_general['algorithm'] = self.model.available_algorithms[self.model.algorithm_name]
    #     self.model.params_general["save_results_file_name"] = self.model.dataset_name + "_" + self.model.algorithm_name
    #     self.view.save_result_file_name.setText(self.model.params_general["save_results_file_name"])
