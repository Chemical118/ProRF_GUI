from ryven.NWENV import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import rcParams
from qtpy.QtWidgets import QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget, QTextEdit
from qtpy.QtGui import QImage, QPixmap, QFont
from qtpy.QtCore import Signal, QSize, QTimer

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')


def nrmse(pre, tru):
    return np.sqrt(np.mean((pre - tru) ** 2)) / (np.max(tru) - np.min(tru))


class XLSXInputWidget(IWB, QPushButton):
    path_chosen = Signal(str)

    def __init__(self, params):
        IWB.__init__(self, params)
        QPushButton.__init__(self, "Select")

        self.clicked.connect(self.button_clicked)

    def button_clicked(self):
        file_path = QFileDialog.getOpenFileName(self, 'Select Excel file', filter="Excel file (*.xlsx)")[0]
        try:
            file_path = os.path.relpath(file_path)
        except ValueError:
            return

        self.path_chosen.emit(file_path)


class FASTAInputWidget(IWB, QPushButton):
    path_chosen = Signal(str)

    def __init__(self, params):
        IWB.__init__(self, params)
        QPushButton.__init__(self, "Select")

        self.clicked.connect(self.button_clicked)

    def button_clicked(self):
        file_path = QFileDialog.getOpenFileName(self, 'Select Fasta file', filter="Fasta file (*.fas;*.fasta)")[0]
        try:
            file_path = os.path.relpath(file_path)
        except ValueError:
            return

        self.path_chosen.emit(file_path)


class FolderInputWidget(IWB, QPushButton):
    path_chosen = Signal(str)

    def __init__(self, params):
        IWB.__init__(self, params)
        QPushButton.__init__(self, "Select")

        self.clicked.connect(self.button_clicked)

    def button_clicked(self):
        file_path = QFileDialog.getExistingDirectory(self, 'Select Dataset folder')
        try:
            file_path = os.path.relpath(file_path)
        except ValueError:
            return

        self.path_chosen.emit(file_path)


class PredictViewWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        self.figure = plt.Figure(figsize=(40, 35))
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.setFixedHeight(350)
        self.setFixedWidth(400)

    def show_result(self, py, y, z=None):
        self.figure.clear()
        rcParams.update({'figure.autolayout': True})
        ax = self.figure.add_subplot(111)
        nrmse_val = nrmse(py, y)

        if z is None:
            ax.scatter(y, py, color="#440154", s=20)
        else:
            im = ax.scatter(y, py, c=z, s=3)
            plt.colorbar(im, ax=ax)

        # ax.set_title("Random Forest Regression Result")
        ax.set_xlabel("True Values")
        ax.set_ylabel("Predictions")
        ax.axis("equal")
        ax.axis("square")
        ax.set_xlim(-max(0, -ax.get_xlim()[0]), ax.get_xlim()[1])
        ax.set_ylim(-max(0, -ax.get_ylim()[0]), ax.get_ylim()[1])
        ax.annotate("NRMSE : %.4f" % nrmse_val, ((np.asarray([0.97, 0.03]) @ np.asarray(ax.get_xlim())),
                                                 (np.asarray([0.05, 0.95]) @ np.asarray(ax.get_ylim()))))
        ax.plot([-1000, 1000], [-1000, 1000], color="black")
        self.canvas.draw()
        return nrmse_val


class ImportanceViewWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        self.figure = plt.Figure(figsize=(40, 35))
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.setFixedHeight(350)
        self.setFixedWidth(400)

    def show_result(self, f, lo, show_number):
        self.figure.clear()
        rcParams.update({'figure.autolayout': True})
        ax = self.figure.add_subplot(111)
        lo = np.asarray(lo)

        data_len = np.size(f)
        f /= np.max(f)
        show_number = min(data_len, show_number)
        sorted_idx = np.argsort(f)[::-1]
        bar_pos = np.asarray(range(data_len, 0, -1)) - 0.5
        ax.barh(bar_pos[0:show_number], f[sorted_idx][0:show_number], align="center")
        ax.set_yticks(bar_pos[0:show_number], lo[sorted_idx][0:show_number])
        ax.set_xlabel("Feature Importance")
        ax.set_ylabel("Amino acid Location")

        self.canvas.draw()


export_widgets(
    XLSXInputWidget,
    FASTAInputWidget,
    FolderInputWidget,
    PredictViewWidget,
    ImportanceViewWidget,
)
