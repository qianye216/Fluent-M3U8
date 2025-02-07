from unittest import TestCase
from pathlib import Path

from app.service.version_service import VersionService


class TestVersionService(TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.service = VersionService()

    def test_has_new_version(self):
        hasNewVersion = self.service.hasNewVersion()
        self.assertFalse(hasNewVersion)
