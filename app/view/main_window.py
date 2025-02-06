# coding: utf-8
from PySide6.QtCore import QUrl, QSize
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtSql import QSqlDatabase

from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen
from qfluentwidgets import FluentIcon as FIF

from .setting_interface import SettingInterface
from .home_interface import HomeInterface
from .task_interface import TaskInterface
from ..common.database import DBInitializer, DatabaseThread, Database
from ..common.config import cfg
from ..common.icon import Icon
from ..common.utils import openUrl
from ..common.signal_bus import signalBus, SqlResponse
from ..common.setting import DOC_URL
from ..service.m3u8dl_service import m3u8Service
from ..common import resource


class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()

        self.initDatabase()
        self.initWindow()

        self.homeInterface = HomeInterface(self)
        self.taskInterface = TaskInterface(self)
        self.settingInterface = SettingInterface(self)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToTaskInterfaceSig.connect(lambda: self.switchTo(self.taskInterface))

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'), FIF.HOME_FILL, isTransparent=True)
        self.addSubInterface(self.taskInterface, Icon.CLOUD_DOWNLOAD, self.tr('Task'), Icon.CLOUD_DOWNLOAD_FILLED)

        self.navigationInterface.addItem(
            'help', FIF.HELP, self.tr("Help"), lambda: openUrl(DOC_URL), False, position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(
            self.settingInterface, Icon.SETTINGS, self.tr('Settings'), Icon.SETTINGS_FILLED, NavigationItemPosition.BOTTOM)

        self.splashScreen.finish()

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/app/images/logo.png'))
        self.setWindowTitle('Fluent M3U8')

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

        signalBus.dataFetched.connect(self._onDataFetched)

    def _onDataFetched(self, response: SqlResponse):
        if response.slot:
            response.slot(response.data)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def closeEvent(self, e):
        m3u8Service.clearTasks()
        super().closeEvent(e)