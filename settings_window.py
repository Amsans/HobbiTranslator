from pathlib import Path

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QDialog, QSlider, QPushButton, QGridLayout, QCheckBox

IMG_PATH = str(Path(__file__).absolute().parent / 'img')


class SettingsWindow(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle('Налады')
        self.setWindowIcon(QIcon(QPixmap(IMG_PATH + '/house.png')))
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('ШРЫФТ'))
        self.isBold = QCheckBox('ТЛУСТЫ')
        self.isBold.setChecked(self.settings.value('main/font-bold', False, type=bool))
        layout.addWidget(self.isBold)
        labelLayout = QGridLayout()
        labelLayout.addWidget(QLabel('4'), 0, 0, 1, 1)
        labelLayout.addWidget(QLabel('33'), 0, 1, 1, 1)
        labelLayout.addWidget(QLabel('63'), 0, 2, 1, 1)
        labelLayout.addWidget(QLabel('93'), 0, 3, 1, 1, Qt.AlignLeft)
        labelLayout.addWidget(QLabel('180'), 0, 3, 1, 1, Qt.AlignRight)
        layout.addLayout(labelLayout)
        self.fontSlider = QSlider(Qt.Horizontal)
        self.fontSlider.setMinimum(4)
        self.fontSlider.setMaximum(180)
        self.fontSlider.setSingleStep(1)
        self.fontSlider.setPageStep(10)
        self.fontSlider.setTickPosition(QSlider.TicksAbove)
        self.fontSlider.setTickInterval(5)
        self.fontSlider.setMinimumHeight(40)
        self.fontSlider.setValue(self.settings.value('main/font', 24))
        layout.addWidget(self.fontSlider)

        btnLayout = QHBoxLayout()
        saveBtn = QPushButton('ЗАХАВАЦЬ')
        saveBtn.setIcon(QIcon(QPixmap(IMG_PATH + '/save.png')))
        saveBtn.setIconSize(QSize(38, 38))
        saveBtn.clicked.connect(self.saveSettings)

        closeBtn = QPushButton('ЗАКРЫЦЬ')
        closeBtn.setIcon(QIcon(QPixmap(IMG_PATH + '/cancel.png')))
        closeBtn.setIconSize(QSize(38, 38))
        closeBtn.clicked.connect(self.close)

        btnLayout.addWidget(saveBtn)
        btnLayout.addWidget(closeBtn)
        layout.addLayout(btnLayout)
        self.setLayout(layout)

    def saveSettings(self):
        self.settings.setValue('main/font', self.fontSlider.value())
        self.settings.setValue('main/font-bold', self.isBold.isChecked())
        self.close()
