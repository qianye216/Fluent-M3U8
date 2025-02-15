from unittest import TestCase

from app.service.m3u8dl_service import M3U8DLService


class TestM3U8DLService(TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.service = M3U8DLService()

    def test_get_stream_infos(self):
        url = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        videos = self.service.getStreamInfos(url)
        self.assertEqual(len(videos), 5)

    def test_get_empty_stream_infos(self):
        url = "https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/hls/xgplayer-demo.m3u8"
        videos = self.service.getStreamInfos(url)
        self.assertEqual(len(videos), 0)

    def test_get_timer_stream_infos(self):
        url = "http://devimages.apple.com/iphone/samples/bipbop/gear1/prog_index.m3u8"
        videos = self.service.getStreamInfos(url)
        self.assertEqual(len(videos), 0)

    def test_get_live_stream_infos(self):
        url = "http://cdn3.toronto360.tv:8081/toronto360/hd/playlist.m3u8"
        videos = self.service.getStreamInfos(url)
        self.assertEqual(len(videos), 1)
