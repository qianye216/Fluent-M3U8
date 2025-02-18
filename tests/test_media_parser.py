from unittest import TestCase

from app.common.media_parser import MediaParser


class TestM3U8DLService(TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_get_stream_infos(self):
        url = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        videos = MediaParser.parse(url).getStreamInfos()
        self.assertEqual(len(videos), 5)

    def test_get_empty_stream_infos(self):
        url = "https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/hls/xgplayer-demo.m3u8"
        videos = MediaParser.parse(url).getStreamInfos()
        self.assertEqual(len(videos), 0)

    def test_get_timer_stream_infos(self):
        url = "http://devimages.apple.com/iphone/samples/bipbop/gear1/prog_index.m3u8"
        videos = MediaParser.parse(url).getStreamInfos()
        self.assertEqual(len(videos), 0)

    def test_get_live_stream_infos(self):
        url = "http://cdn3.toronto360.tv:8081/toronto360/hd/playlist.m3u8"
        videos = MediaParser.parse(url).getStreamInfos()
        self.assertEqual(len(videos), 1)

    def test_get_encrypted_live_stream_infos(self):
        url = "https://bcovlive-a.akamaihd.net/17789746e9e8477dbcdf8ceb96926d3b/ap-northeast-1/6160987587001/profile_0/chunklist_wv.m3u8"
        key = "98fe2cc47352f0170a03d2eeb41d0488:9b35588ce16dc0894af4fdd5a01abcb5"
        videos = MediaParser.parse(url).getStreamInfos()
        self.assertEqual(len(videos), 0)

    def test_mpd_stream_infos(self):
        url = "http://yt-dash-mse-test.commondatastorage.googleapis.com/media/motion-20120802-manifest.mpd"
        videos = MediaParser.parse(url).getStreamInfos()
        self.assertEqual(len(videos), 5)
