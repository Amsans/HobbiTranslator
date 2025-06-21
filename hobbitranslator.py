import sys
import json
from pathlib import Path
from PyQt5.QtCore import Qt, QSize, QSettings, QByteArray, QUrl, QJsonDocument
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QMovie
from PyQt5.QtWidgets import QApplication, QStyleFactory, QMainWindow, QWidget, QGridLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QMessageBox, QComboBox, QLabel
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from settings_window import SettingsWindow

IMG_PATH = str(Path(__file__).absolute().parent / 'img')
AUTH_KEY = ''


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)
        self.worker_url = 'https://deepl-proxy.amra-team.workers.dev'
        self.settings = QSettings('AmraSoft', 'Hobbit Translator')
        self.settingsWindow = None
        self.translatedResult = None

        # Initialize QNetworkAccessManager
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.handle_network_reply)

        self.setWindowTitle("Перакладчык Хобіт: Туды і назад v1.3")
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

    def show_loading(self):
        if not hasattr(self, 'loading_overlay'):
            self.loading_overlay = QWidget(self.centralWidget())
            self.loading_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 128);")
            self.loading_overlay.setGeometry(0, 0, self.centralWidget().width(), self.centralWidget().height())
            self.loading_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.loading_overlay.setWindowFlags(Qt.FramelessWindowHint)

            self.spinner_label = QLabel(self.loading_overlay)
            self.spinner = QMovie(IMG_PATH + "/spinner.gif")
            self.spinner_label.setMovie(self.spinner)
            self.spinner_label.setAlignment(Qt.AlignCenter)
            self.spinner_label.setGeometry(0, 0, self.centralWidget().width(), self.centralWidget().height())

        self.loading_overlay.setGeometry(0, 0, self.centralWidget().width(), self.centralWidget().height())
        self.loading_overlay.raise_()
        self.loading_overlay.setVisible(True)
        self.spinner.start()
        QApplication.processEvents()

    def hide_loading(self):
        if hasattr(self, 'loading_overlay'):
            self.spinner.stop()
            self.loading_overlay.setVisible(False)
            QApplication.processEvents()

    def performTranslate(self):
        text = self.sourceTextEdit.toPlainText()
        if not text:
            return

        self.show_loading()
        self.sourceTextEdit.setEnabled(False)
        self.targetTextEdit.setEnabled(False)
        self.translateBtn.setEnabled(False)
        self.copyBtn.setEnabled(False)

        # Prepare async request
        request = QNetworkRequest(QUrl(self.worker_url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        request.setRawHeader(b"Hobbit-Token", AUTH_KEY.encode('utf-8'))
        data = QJsonDocument.fromJson(json.dumps({'text': text, 'target_lang': 'EN-GB'}).encode('utf-8'))

        # Send async request
        self.network_manager.post(request, data.toJson())

    def handle_network_reply(self, reply):
        try:
            if reply.error() != QNetworkReply.NoError:
                error_msg = f"Error: {reply.errorString()}"
                if reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) == 400:
                    error_msg = "Translation failed: Invalid request to DeepL"
                    try:
                        error_details = json.loads(reply.readAll().data().decode('utf-8'))
                        error_msg += f" - {error_details.get('message', 'No details provided')}"
                    except ValueError:
                        pass
                self.targetTextEdit.setPlainText(error_msg)
                print(error_msg)
            else:
                response_data = reply.readAll().data().decode('utf-8')
                data = json.loads(response_data)
                self.targetTextEdit.setPlainText(data['back_translation'])
                self.translatedResult = data['first_translation']

        except Exception as e:
            error_msg = f"Error processing response: {e}"
            self.targetTextEdit.setPlainText(error_msg)
            print(error_msg)

        finally:
            self.sourceTextEdit.setEnabled(True)
            self.targetTextEdit.setEnabled(True)
            self.translateBtn.setEnabled(True)
            self.copyBtn.setEnabled(True)
            self.hide_loading()
            reply.deleteLater()

    def performCopy(self):
        clipboard = QApplication.clipboard()
        if self.translatedResult:
            clipboard.clear(mode=clipboard.Clipboard)
            clipboard.setText(self.translatedResult, mode=clipboard.Clipboard)

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

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
