from unittest import TestCase
from pathlib import Path

from app.service.m3u8dl_service import M3U8DLCommandLineParser


class TestCommandLineParser(TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.parser = M3U8DLCommandLineParser()

    def test_binary_merge(self):
        cmd1 = "https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/hls/xgplayer-demo.m3u8 --save-name=test --save-dir=/Users/shokokawaii/Downloads --tmp-dir=/Users/shokokawaii/Downloads --thread-count=10 --http-request-timeout=100 --download-retry-count=3 --sub-format=SRT --auto-select=False --binary-merge=False --del-after-done=True --append-url-params=False --no-date-info=False --concurrent-download=False"
        task1 = self.parser.parse(cmd1.split(" "))
        self.assertFalse(task1.isBinaryMerge)

        cmd2 = "https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/hls/xgplayer-demo.m3u8 --save-name=test --save-dir=/Users/shokokawaii/Downloads --tmp-dir=/Users/shokokawaii/Downloads --thread-count=10 --http-request-timeout=100 --download-retry-count=3 --sub-format=SRT --auto-select=False --binary-merge=True --del-after-done=True --append-url-params=False --no-date-info=False --concurrent-download=False"
        task2 = self.parser.parse(cmd2.split())
        self.assertTrue(task2.isBinaryMerge)
