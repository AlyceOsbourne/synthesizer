# algorithm to create a dict of notes and frequencies
# and then create a sine wave
from enum import Enum
from functools import cache
import numpy as np
from matplotlib import pyplot as plt
from audio_manager import AudioStream


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
    @cache
    def _frequency(value, octave):
        return 440 * 2 ** ((value + octave - 4) / 12)

    def frequency(self, octave):
        return Note._frequency(self.value, octave)


def sine_wave(frequency, sample_rate):
    period = sample_rate / frequency
    while True:
        for x in range(int(period)):
            yield np.sin(2 * np.pi * x / period)


def square_wave(frequency, sample_rate):
    period = sample_rate / frequency
    while True:
        for x in range(int(period)):
            if x < period / 2:
                yield 1
            elif x > period / 2:
                yield -1
            else:
                yield 0


def triangle_wave(frequency, sample_rate):
    period = sample_rate / frequency
    while True:
        for x in range(int(period)):
            yield 2 * (x % int(period / 2)) / int(period / 2) - 1


def sawtooth_wave(frequency, sample_rate):
    period = sample_rate / frequency
    while True:
        for x in range(int(period)):
            yield 2 * (x % int(period)) / int(period) - 1


@cache
def notes_dict():
    return {f"{note.notation}:{octave}" : note.frequency(octave) for note in Note for octave in range(0, 11)}

@cache
def create_wave_generators(sample_rate=44100):
    return {f"{wave_function.__name__}:{note}": wave_function(frequency, sample_rate)
            for wave_function in [sine_wave, square_wave, triangle_wave, sawtooth_wave]
            for note, frequency in notes_dict().items()}


