# coding: utf-8
from enum import Enum

from qfluentwidgets import FluentIconBase, getIconColor, Theme


class Icon(FluentIconBase, Enum):

    SETTINGS = "Settings"
    SETTINGS_FILLED = "SettingsFilled"

    def path(self, theme=Theme.AUTO):
        return f":/app/images/icons/{self.value}_{getIconColor(theme)}.svg"


class Ico(FluentIconBase, Enum):

    M3U8DL = "M3U8DL"

    def path(self, theme=Theme.AUTO):
        return f":/app/images/icos/{self.value}.ico"


class Logo(FluentIconBase, Enum):

    FILM = "Film"
    MOON = "Moon"
    KNOT = "Knot"
    LINK = "Link"
    GLOBE = "Globe"
    WHALE = "Whale"
    LABEL = "Label"
    BROOM = "Broom"
    COOKIE = "Cookie"
    HAMMER = "Hammer"
    OFFICE = "Office"
    PENCIL = "Pencil"
    MONKEY = "Monkey"
    FOLDER = "Folder"
    ROCKET = "Rocket"
    SCROLL = "Scroll"
    WINDOW = "Window"
    ALEMBIC = "Alembic"
    PACKAGE = "Package"
    BOOKMARK = "Bookmark"
    TERMINAL = "Terminal"
    JOYSTICK = "Joystick"
    BAR_CHART = "BarChart"
    HOURGLASS = "Hourglass"
    WASTEBASKET = "Wastebasket"
    CARD_FILE_BOX = "CardFileBox"

    def path(self, theme=Theme.AUTO) -> str:
        return f":/app/images/logo/{self.value}.svg"
