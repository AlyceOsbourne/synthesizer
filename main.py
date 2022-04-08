# algorithm to create a dict of notes and frequencies
# and then create a sine wave
import time
from enum import Enum, auto
from math import pi, log2
from functools import partial, cache

import numpy as np
from pyaudio import paInt32, PyAudio

FORMAT = paInt32
CHANNELS = 1
RATE = 44100
CHUNK = 1024


class Note(Enum):
    A = 0, 'A'
    A_SHARP = 1, 'A#'
    B = 2, 'B'
    C = 3, 'C'
    C_SHARP = 4, 'C#'
    D = 5, 'D'
    D_SHARP = 6, 'D#'
    E = 7, 'E'
    F = 8, 'F'
    F_SHARP = 9, 'F#'
    G = 10, 'G'
    G_SHARP = 11, 'G#'

    def __new__(cls, value, notation):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.notation = notation
        return obj

    @staticmethod
    def _frequency(value, octave):
        return 440 * 2 ** ((value + octave - 4) / 12)

    @cache
    def frequency(self, octave):
        return self._frequency(self.value, octave)

    @staticmethod
    def _sine(frequency, duration, sample_rate):
        samples = int(sample_rate * duration)
        sine_wave = np.sin(2 * pi * frequency * np.arange(samples) / sample_rate)
        return sine_wave.astype(np.float32)

    @cache
    def sine(self, octave, duration, sample_rate):
        return self._sine(self.frequency(octave), duration, sample_rate)

    @staticmethod
    def _square(frequency, duration, sample_rate):
        samples = int(sample_rate * duration)
        sine_wave = np.sin(2 * pi * frequency * np.arange(samples) / sample_rate)
        square_wave = sine_wave.astype(np.float32)
        square_wave[square_wave > 0] = 1
        square_wave[square_wave < 0] = -1
        return square_wave

    @cache
    def square(self, octave, duration, sample_rate):
        return self._square(self.frequency(octave), duration, sample_rate)

    @staticmethod
    def _sawtooth(frequency, duration, sample_rate):
        samples = int(sample_rate * duration)
        sine_wave = np.sin(2 * pi * frequency * np.arange(samples) / sample_rate)
        sawtooth_wave = sine_wave.astype(np.float32)
        sawtooth_wave[sawtooth_wave > 0] = 1
        sawtooth_wave[sawtooth_wave < 0] = -1
        return sawtooth_wave

    @cache
    def sawtooth(self, octave, duration, sample_rate):
        return self._sawtooth(self.frequency(octave), duration, sample_rate)

    @staticmethod
    def _triangle(frequency, duration, sample_rate):
        samples = int(sample_rate * duration)
        sine_wave = np.sin(2 * pi * frequency * np.arange(samples) / sample_rate)
        triangle_wave = sine_wave.astype(np.float32)
        triangle_wave[triangle_wave > 0] = 1
        triangle_wave[triangle_wave < 0] = -1
        triangle_wave = triangle_wave * 2 - 1
        return triangle_wave

    @cache
    def triangle(self, octave, duration, sample_rate):
        return self._triangle(self.frequency(octave), duration, sample_rate)


@cache
def pyaudio_context():
    return PyAudio()


@cache
def pyaudio_stream():
    return pyaudio_context().open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True,
                                  frames_per_buffer=CHUNK)


def close_stream():
    pyaudio_stream().close()
    pyaudio_stream.cache_clear()


def play_note(note, octave, duration, sample_rate=RATE, wave_type="sine"):
    stream = pyaudio_stream()
    stream.write(getattr(note, wave_type)(octave, duration, sample_rate))


def play_chord(notes: list[tuple[Note, int]], duration, sample_rate=RATE, wave_type="sine"):
    # add two waves together using numpy
    stream = pyaudio_stream()
    chord = None
    for note, octave in notes:
        if chord is None:
            chord = getattr(note, wave_type)(octave, duration, sample_rate)
        else:
            chord += getattr(note, wave_type)(octave, duration, sample_rate)

    stream.write(chord.tobytes())


def play_sequence(notes, octaves, durations, sample_rate=RATE, wave_type="sine"):
    stream = pyaudio_stream()
    for note, octave, duration in zip(notes, octaves, durations):
        stream.write(getattr(note, wave_type)(octave, duration, sample_rate))
        time.sleep(duration)


def play_chord_sequence(notes: list[list[tuple[Note, int]]], durations, delay, sample_rate=RATE, wave_type="sine"):
    for notes, duration in zip(notes, durations):
        play_chord(notes, duration, sample_rate, wave_type)
        time.sleep(delay)


def play_song(song, sample_rate=RATE, wave_type="sine"):
    for note, octave, duration in song:
        play_note(note, octave, duration, sample_rate, wave_type)


song = (
    (Note.C, 4, 0.5),
    (Note.D, 4, 0.5),
    (Note.E, 4, 0.5),
    (Note.F, 4, 0.5),
    (Note.G, 4, 0.5),
    (Note.A, 4, 0.5),
    (Note.B, 4, 0.5),
    (Note.C, 5, 0.5),

)

play_song(song, wave_type="triangle")

play_chord_sequence(
    notes=[
    [(Note.C, 4), (Note.F, 4), (Note.G, 4)],
    [(Note.C, 4), (Note.A, 4), (Note.D_SHARP, 4)],
    [(Note.C, 4), (Note.D, 4), (Note.E, 4)],
    [(Note.C, 4), (Note.D, 4), (Note.F, 4)],
    [(Note.C, 4), (Note.D, 4), (Note.G, 4)]
],
    durations=[0.5, 0.5, 0.5, 0.5, 0.5],
    delay=0.5,
    wave_type="sawtooth")
