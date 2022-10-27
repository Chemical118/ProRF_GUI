from ryven.NWENV import *
from qtpy.QtWidgets import QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget, QTextEdit
from qtpy.QtGui import QImage, QPixmap, QFont
from qtpy.QtCore import Signal, QSize, QTimer

import os


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


export_widgets(
    XLSXInputWidget,
    FASTAInputWidget,
    FolderInputWidget,
)
