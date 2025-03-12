# coding:utf-8
from dataclasses import dataclass
from typing import List

import m3u8
from m3u8 import M3U8
from mpegdash.parser import MPEGDASHParser, MPEGDASH
from mpegdash.nodes import Period, AdaptationSet, Representation

from ..common.exception_handler import exceptionTracebackHandler
from ..common.logger import Logger


@dataclass
class StreamInfo:
    """ Media stream info """
    resolution: tuple = None
    codecs: str = None
    frame_rate: float = None


class MediaParser:
    """ Media parser base class """

    formats = []
    parsers = []

    def __init__(self, url: str):
        self.url = url
        self.isParsed = False

    def _parse(self):
        raise NotImplementedError

    @classmethod
    def canParse(cls, url: str) -> bool:
        """ determine whether song information of the file can be read """
        return url.lower().endswith(tuple(cls.formats))

    def getStreamInfos(self) -> List[StreamInfo]:
        raise NotImplementedError

    def isLive(self):
        return False

    @classmethod
    def register(cls, parser):
        """ register song information parser

        Parameters
        ----------
        parser:
            media parser class
        """
        if parser not in cls.parsers:
            cls.parsers.append(parser)
            cls.formats.extend(parser.formats)

        return parser

    @classmethod
    def parse(cls, url: str) -> 'MediaParser':
        for Parser in cls.parsers:
            if Parser.canParse(url):
                return Parser(url)

        Logger("download").warning(f"No media parser available for `{url}`")
        return None


@MediaParser.register
class M3U8MediaParser(MediaParser):
    """ M3U8 media parser """

    formats = [".m3u8", ".m3u"]

    def __init__(self, url):
        super().__init__(url)
        self.m3u8 = None    # type: M3U8

    def _parse(self):
        self.m3u8 = m3u8.load(self.url, timeout=3)

    @exceptionTracebackHandler("download", [])
    def getStreamInfos(self) -> List[StreamInfo]:
        if not self.m3u8:
            self._parse()

        if not self.m3u8.playlists:
            return []

        streamInfos = []
        for playlist in self.m3u8.playlists:
            streamInfos.append(StreamInfo(
                resolution=playlist.stream_info.resolution,
                codecs=playlist.stream_info.codecs,
                frame_rate=playlist.stream_info.frame_rate,
            ))

        return streamInfos

    @exceptionTracebackHandler("download", False)
    def isLive(self):
        if not self.m3u8:
            self._parse()

        return not self.m3u8.is_endlist


@MediaParser.register
class MPDMediaParser(MediaParser):
    """ MPD media parser """

    formats = [".mpd"]

    def __init__(self, url):
        super().__init__(url)
        self.mpd = None    # type: MPEGDASH

    def _parse(self):
        self.mpd = MPEGDASHParser.parse(self.url)

    @exceptionTracebackHandler("download", [])
    def getStreamInfos(self) -> List[StreamInfo]:
        if not self.mpd:
            self._parse()

        if not self.mpd.periods:
            return []

        streamInfos = []

        for adaptation_set in self.mpd.periods[0].adaptation_sets:
            for represent in adaptation_set.representations:
                if not self._isVideo(adaptation_set, represent):
                    continue

                # parse frame rate
                frame_rate = represent.frame_rate   # type: str
                if frame_rate is not None:
                    if frame_rate.find("/") != -1:
                        num, den = frame_rate.split("/")
                        frame_rate = float(int(num)/int(den))
                    else:
                        frame_rate = float(frame_rate)

                if represent.width:
                    streamInfos.append(StreamInfo(
                        resolution=(represent.width, represent.height),
                        codecs=represent.codecs,
                        frame_rate=frame_rate,
                    ))

        return streamInfos

    def _isVideo(self, adaptation_set: AdaptationSet, represent: Representation):
        if adaptation_set.content_type and adaptation_set.content_type.lower() == "video":
            return True

        mime_type = adaptation_set.mime_type or represent.mime_type
        if mime_type and mime_type.lower().startswith("video"):
            return True

        if represent.id and represent.id.find("video") >= 0:
            return True

        return False

    @exceptionTracebackHandler("download", False)
    def isLive(self):
        if not self.mpd:
            self._parse()

        return self.mpd.type == "dynamic"
