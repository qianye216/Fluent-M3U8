# coding: utf-8
from PySide6.QtCore import QUrl, QSize, Qt
from PySide6.QtGui import QIcon, QColor, QGuiApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtSql import QSqlDatabase

from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen, MessageBox, InfoBarIcon
from qfluentwidgets import FluentIcon as FIF

from .setting_interface import SettingInterface
from .home_interface import HomeInterface
from .task_interface import TaskInterface
from ..common.database import DBInitializer, DatabaseThread, Database
from ..common.config import cfg
from ..common.icon import Icon
from ..common.utils import openUrl
from ..common.signal_bus import signalBus, SqlResponse
from ..common.setting import DOC_URL, FEEDBACK_URL
from ..service.m3u8dl_service import m3u8Service, Task
from ..components.system_tray_icon import SystemTrayIcon
from ..common import resource


class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()

        self.initDatabase()
        self.initWindow()

        self.homeInterface = HomeInterface(self)
        self.taskInterface = TaskInterface(self)
        self.settingInterface = SettingInterface(self)
        self.systemTrayIcon = SystemTrayIcon(self)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToTaskInterfaceSig.connect(lambda: self.switchTo(self.taskInterface))
        signalBus.appErrorSig.connect(self.onAppError)
        signalBus.appMessageSig.connect(self.onAppMessage)

        m3u8Service.downloadFinished.connect(self.onDownloadFinished)

        self.systemTrayIcon.messageClicked.connect(self.onSystemTrayMessageClicked)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'), FIF.HOME_FILL, isTransparent=True)
        self.addSubInterface(self.taskInterface, Icon.CLOUD_DOWNLOAD, self.tr('Task'), Icon.CLOUD_DOWNLOAD_FILLED)

        self.navigationInterface.addItem(
            'help', FIF.HELP, self.tr("Help"), lambda: openUrl(DOC_URL), False, position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(
            self.settingInterface, Icon.SETTINGS, self.tr('Settings'), Icon.SETTINGS_FILLED, NavigationItemPosition.BOTTOM)

        self.splashScreen.finish()
        self.systemTrayIcon.show()

    def initWindow(self):
        self.resize(960, 773)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/app/images/logo.png'))
        self.setWindowTitle('Fluent M3U8')
        QApplication.setQuitOnLastWindowClosed(False)

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def initDatabase(self):
        """ initialize song library """
        DBInitializer.init()

        self.databaseThread = DatabaseThread(
            QSqlDatabase.database(DBInitializer.CONNECTION_NAME), self)

        signalBus.dataFetched.connect(self.onDataFetched)

    def onDataFetched(self, response: SqlResponse):
        if response.slot:
            response.slot(response.data)

    def onAppError(self, message: str):
        """ app error slot """
        QApplication.clipboard().setText(message)
        self.showMessageBox(
            self.tr("Unhandled exception occurred"),
            self.tr("The error message has been written to the paste board and log. Do you want to report?"),
            True,
            lambda: openUrl(FEEDBACK_URL)
        )

    def onAppMessage(self, message: str):
        if message == "show":
            if self.windowState() & Qt.WindowMinimized:
                self.showNormal()
            else:
                self.show()
        else:
            # TODO: parse command line args

            self.switchTo(self.homeInterface)
            self.show()

    def showMessageBox(self, title: str, content: str, showYesButton=False, yesSlot=None):
        """ show message box """
        w = MessageBox(title, content, self)
        if not showYesButton:
            w.cancelButton.setText(self.tr('Close'))
            w.yesButton.hide()
            w.buttonLayout.insertStretch(0, 1)

        if w.exec() and yesSlot is not None:
            yesSlot()

    def onDownloadFinished(self, task: Task, success: bool, errorMsg: str):
        if success:
            self.systemTrayIcon.showMessage(
                self.tr("Task finished"),
                f'"{task.fileName}"' + self.tr("download successfully"),
                InfoBarIcon.SUCCESS.qicon()
            )
        else:
            self.systemTrayIcon.showMessage(
                self.tr("Task failed"),
                f'"{task.fileName}"' + self.tr("download failed") + ": " + errorMsg,
                InfoBarIcon.ERROR.qicon()
            )

    def onSystemTrayMessageClicked(self):
        self.switchTo(self.taskInterface)
        self.taskInterface.stackedWidget.setCurrentIndex(1)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def onExit(self):
        """ exit main window """
        self.systemTrayIcon.hide()

        # clear tasks
        m3u8Service.clearTasks()

        # close database
        QSqlDatabase.database(DBInitializer.CONNECTION_NAME).close()
        QSqlDatabase.removeDatabase(DBInitializer.CONNECTION_NAME)