# coding:utf-8
from pathlib import Path
import subprocess
import sys
from PySide6.QtCore import QObject

import ffmpeg
from ffmpeg._run import output_operator

from ..common.config import cfg
from ..common.utils import removeFile


# monkey patch
@output_operator()
def patched_run_async(
    stream_spec,
    cmd='ffmpeg',
    pipe_stdin=False,
    pipe_stdout=False,
    pipe_stderr=False,
    quiet=False,
    overwrite_output=False,
):
    # hide windows console
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NO_WINDOW

    args = ffmpeg._run.compile(stream_spec, cmd, overwrite_output=overwrite_output)
    stdin_stream = subprocess.PIPE if pipe_stdin else None
    stdout_stream = subprocess.PIPE if pipe_stdout or quiet else None
    stderr_stream = subprocess.PIPE if pipe_stderr or quiet else None
    return subprocess.Popen(
        args, stdin=stdin_stream, stdout=stdout_stream, stderr=stderr_stream, creationflags=creationflags
    )

ffmpeg._run.run_async = patched_run_async


class FFmpegService(QObject):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def saveVideoCover(self, videoPath: Path | str, savePath: Path | str):
        if Path(savePath).exists():
            removeFile(savePath)

        ffmpeg.input(str(videoPath), ss=0).output(str(savePath), vframes=1, loglevel="quiet").run(self.path)

    @property
    def path(self):
        return cfg.get(cfg.ffmpegPath)



ffmpegService = FFmpegService()