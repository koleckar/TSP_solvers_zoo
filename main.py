from view import MainWindow
from controller import Controller
from model import Model

from PyQt5 import QtWidgets
import sys


def main():
    # QApplication has to be called before QMainWindow !
    app = QtWidgets.QApplication(sys.argv)
    view = MainWindow()
    model = Model("berlin52.tsp", "ea")
    controller = Controller(view, model)

    app.exec_()


if __name__ == "__main__":
    main()
