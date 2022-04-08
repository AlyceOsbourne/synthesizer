from functools import cache

from pyaudio import paInt32, PyAudio

FORMAT = paInt32
CHANNELS = 1
RATE = 44100
CHUNK = 1024


class AudioStream:
    def __init__(self, data_format=FORMAT, channels=CHANNELS, rate=RATE, chunk=CHUNK):
        self.format = data_format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk

    @staticmethod
    @cache
    def pyaudio_context():
        return PyAudio()

    @cache
    def pyaudio_stream(self):
        return self.pyaudio_context().open(format=self.format,
                                           channels=self.channels,
                                           rate=self.rate,
                                           output=True,
                                           frames_per_buffer=self.chunk)

    def __enter__(self):
        return self.pyaudio_stream()

    def __exit__(self, exc_type, exc_value, traceback):
        self.pyaudio_stream().stop_stream()
        self.pyaudio_stream().close()
        self.pyaudio_stream.cache_clear()

    def play(self, samples):
        self.pyaudio_stream().write(samples)
