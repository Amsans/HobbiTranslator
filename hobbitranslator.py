import sys
from pathlib import Path

import deepl
from PyQt5.QtCore import Qt, QSize, QSettings, QByteArray
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QStyleFactory, QMainWindow, QWidget, QGridLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QMessageBox, \
    QComboBox

from settings_window import SettingsWindow

IMG_PATH = str(Path(__file__).absolute().parent / 'img')
AUTH_KEY = 'feba98ba-ad9c-4d93-81b6-2aa2ded8ed30:fx'


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)
        self.settings = QSettings('AmraSoft', 'Hobbit Translator')
        self.settingsWindow = None
        self.translator = deepl.Translator(AUTH_KEY)
        self.translatedResult = None

        self.setWindowTitle("Перакладчык Хобіт: Туды і назад v1.1")
        self.setWindowIcon(QIcon(QPixmap(IMG_PATH + '/house.png')))
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        savedGeometry = self.settings.value('main/geometry', QByteArray())
        if not savedGeometry.isEmpty():
            self.restoreGeometry(savedGeometry)

        self.sourceTextEdit = None
        self.targetTextEdit = None
        self.languageCb = None
        self.clearBtn = None
        self.translateBtn = None
        self.copyBtn = None
        self.settingsBtn = None
        self.font = QFont()
        self.font.setBold(self.settings.value('main/font-bold', False, type=bool))
        self.font.setPointSize(self.settings.value('main/font', 24))

        container = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(self.createSourceEdit(), 14)

        centerLayout = QGridLayout()
        centerLayout.addWidget(self.createLanguageCb(), 0, 0, 1, 1, Qt.AlignCenter | Qt.AlignTop)
        centerLayout.addWidget(self.createClearBtn(), 1, 0, 1, 1, Qt.AlignCenter)
        centerLayout.addWidget(self.createTranslateBtn(), 2, 0, 1, 1, Qt.AlignCenter | Qt.AlignBottom)
        centerLayout.addWidget(self.createCopyBtn(), 3, 0, 1, 1, Qt.AlignCenter | Qt.AlignTop)
        centerLayout.addWidget(self.createSettingsBtn(), 4, 0, 1, 1, Qt.AlignCenter)
        layout.addLayout(centerLayout, 1)

        layout.addWidget(self.createTargetEdit(), 14)

        container.setLayout(layout)
        self.setCentralWidget(container)

    def createTargetEdit(self):
        self.targetTextEdit = QPlainTextEdit()
        self.targetTextEdit.setPlainText('')
        self.targetTextEdit.setFont(self.font)
        self.targetTextEdit.setReadOnly(True)
        return self.targetTextEdit

    def createSourceEdit(self):
        self.sourceTextEdit = QPlainTextEdit()
        self.sourceTextEdit.setPlainText('')
        self.sourceTextEdit.setFont(self.font)
        return self.sourceTextEdit

    def createLanguageCb(self):
        self.languageCb = QComboBox()
        self.languageCb.setEnabled(False)
        self.languageCb.addItem('EN')
        self.languageCb.setMinimumHeight(38)
        return self.languageCb

    def createClearBtn(self):
        self.clearBtn = QPushButton('АЧЫСЬЦІЦЬ')
        self.clearBtn.setIconSize(QSize(38, 38))
        self.clearBtn.setIcon(QIcon(QPixmap(IMG_PATH + '/clear.png')))
        self.clearBtn.clicked.connect(self.cleanText)
        return self.clearBtn

    def cleanText(self):
        self.sourceTextEdit.setPlainText('')
        self.targetTextEdit.setPlainText('')

    def createTranslateBtn(self):
        self.translateBtn = QPushButton('ПЕРАКЛАД')
        self.translateBtn.setIconSize(QSize(38, 38))
        self.translateBtn.setIcon(QIcon(QPixmap(IMG_PATH + '/gold_ring.png')))
        self.translateBtn.clicked.connect(self.performTranslate)
        return self.translateBtn

    def createCopyBtn(self):
        self.copyBtn = QPushButton('   У БУФЕР  ')
        self.copyBtn.setIconSize(QSize(38, 38))
        self.copyBtn.setIcon(QIcon(QPixmap(IMG_PATH + '/copy.png')))
        self.copyBtn.setMinimumWidth(136)
        self.copyBtn.setStyleSheet('QPushButton:disabled{color:grey}')
        self.copyBtn.clicked.connect(self.performCopy)
        return self.copyBtn

    def createSettingsBtn(self):
        self.settingsBtn = QPushButton(' НАЛАДЫ ')
        self.settingsBtn.setIconSize(QSize(38, 38))
        self.settingsBtn.setIcon(QIcon(QPixmap(IMG_PATH + '/gear.png')))
        self.settingsBtn.setMinimumWidth(136)
        self.settingsBtn.clicked.connect(self.openSettingDialog)
        return self.settingsBtn

    def performTranslate(self):
        self.sourceTextEdit.setEnabled(False)
        self.targetTextEdit.setEnabled(False)
        self.translateBtn.setEnabled(False)
        self.copyBtn.setEnabled(False)

        # Translate THERE
        text = self.sourceTextEdit.toPlainText()
        self.translatedResult = self.translator.translate_text(text=text, source_lang='RU', target_lang='EN-GB')

        # Translate BACK AGAIN
        result = self.translator.translate_text(text=self.translatedResult.text, source_lang='EN', target_lang='RU')
        self.targetTextEdit.setPlainText(result.text)

        self.sourceTextEdit.setEnabled(True)
        self.targetTextEdit.setEnabled(True)
        self.translateBtn.setEnabled(True)
        self.copyBtn.setEnabled(True)
        self.setEnabled(True)

    def performCopy(self):
        clipboard = QApplication.clipboard()
        if self.translatedResult:
            clipboard.clear(mode=clipboard.Clipboard)
            clipboard.setText(self.translatedResult.text, mode=clipboard.Clipboard)

    def openSettingDialog(self):
        self.settingsWindow = SettingsWindow(self.settings)
        self.settingsWindow.fontSlider.valueChanged.connect(self.changeFontSize)
        self.settingsWindow.isBold.toggled.connect(self.changeFontBold)
        self.settingsWindow.show()

    def changeFontSize(self, value):
        self.font.setPointSize(value)
        self.sourceTextEdit.setFont(self.font)
        self.targetTextEdit.setFont(self.font)

    def changeFontBold(self, value):
        self.font.setBold(value)
        self.sourceTextEdit.setFont(self.font)
        self.targetTextEdit.setFont(self.font)

    def closeEvent(self, event):
        message = QMessageBox()
        message.setWindowIcon(QIcon(QPixmap(IMG_PATH + '/house.png')))
        message.setWindowTitle('Выхад')
        message.setText('Сапраўды хочаце выйсьці?')
        message.setIcon(QMessageBox.Icon.Question)
        message.addButton('Так', QMessageBox.AcceptRole)
        message.addButton('Не', QMessageBox.RejectRole)
        answer = message.exec()
        if answer == 0:
            self.settings.beginGroup('main')
            self.settings.setValue('geometry', self.saveGeometry())
            self.settings.endGroup()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    app.setStyleSheet('QPushButton {font-weight: bold}'
                      'QCheckBox {font-weight: bold}'
                      'QComboBox {font-weight: bold}'
                      'QLabel {font-weight: bold}')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
