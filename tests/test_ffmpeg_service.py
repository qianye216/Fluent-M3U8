from unittest import TestCase
from pathlib import Path

from app.service.ffmpeg_service import FFmpegService


class TestFFmpegService(TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.service = FFmpegService()

    def test_get_stream_infos(self):
        video = "/Users/shokokawaii/Downloads/西瓜视频.mp4"
        savePath = Path("tests/cover.png")
        self.service.saveVideoCover(video, savePath)
        self.assertTrue(savePath.exists())
