from unittest import TestCase

from app.service.m3u8dl_service import M3U8DLService


class TestM3U8DLService(TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.service = M3U8DLService()

    def test_get_stream_infos(self):
        url = "https://cdn3.turboviplay.cc/data2/qnUYIY7y53M4dhaYac3i/qnUYIY7y53M4dhaYac3i.m3u8"
        videos = self.service.getStreamInfos(url)
        self.assertEqual(len(videos), 3)

    def test_get_empty_stream_infos(self):
        url = "https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/hls/xgplayer-demo.m3u8"
        videos = self.service.getStreamInfos(url)
        self.assertEqual(len(videos), 0)
