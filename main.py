# algorithm to create a dict of notes and frequencies
# and then create a sine wave
import time
from enum import Enum
from functools import cache, partial

import numpy as np
from pyaudio import paInt32, PyAudio
import keyboard

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
        sine_wave = np.sin(2 * np.pi * frequency * np.arange(samples) / sample_rate)
        return sine_wave.astype(np.float32)

    @cache
    def sine(self, octave, duration, sample_rate):
        return self._sine(self.frequency(octave), duration, sample_rate)

    # square wave
    @staticmethod
    def _square(frequency, duration, sample_rate):
        samples = int(sample_rate * duration)
        square_wave = np.zeros(samples, dtype=np.float32)
        for i in range(samples):
            if i % (sample_rate // frequency) < sample_rate // frequency / 2:
                square_wave[i] = 1
            else:
                square_wave[i] = -1
        return square_wave

    @cache
    def square(self, octave, duration, sample_rate):
        return self._square(self.frequency(octave), duration, sample_rate)

    @staticmethod
    def _triangle_wave(frequency, duration, sample_rate):
        # output must be between -1 and 1
        samples = int(sample_rate * duration)
        triangle_wave = np.zeros(samples, dtype=np.float32)
        for i in range(samples):
            if i % (sample_rate // frequency) < sample_rate // frequency / 2:
                triangle_wave[i] = 2 * (i % (sample_rate // frequency) / (sample_rate // frequency)) - 1
            else:
                triangle_wave[i] = 2 * (1 - (i % (sample_rate // frequency) / (sample_rate // frequency))) - 1

        # scale to -1 to 1
        return triangle_wave * 2 + 1

    @cache
    def triangle(self, octave, duration, sample_rate):
        return self._triangle_wave(self.frequency(octave), duration, sample_rate)

    # sawtooth wave
    @staticmethod
    def _sawtooth(frequency, duration, sample_rate):
        samples = int(sample_rate * duration)
        sawtooth_wave = np.zeros(samples, dtype=np.float32)
        for i in range(samples):
            sawtooth_wave[i] = 2 * (i % (sample_rate // frequency) / (sample_rate // frequency)) - 1
        return sawtooth_wave

    @cache
    def sawtooth(self, octave, duration, sample_rate):
        return self._sawtooth(self.frequency(octave), duration, sample_rate)

    @cache
    def wave(self, octave, wave_function, duration, sample_rate):
        return getattr(self, wave_function)(octave, duration, sample_rate)

    @staticmethod
    def _oscillator(note, octave, wave_function, duration, sample_rate):
        while True:
            yield getattr(note, wave_function)(octave, duration, sample_rate)

    def oscillator(self, wave_function, octave, duration, sample_rate):
        yield from self._oscillator(self, octave, wave_function, duration, sample_rate)

    @staticmethod
    def _oscillators(note, octave, wave_functions, duration, sample_rate):
        return [getattr(note, wave_function)(octave, duration, sample_rate) for wave_function in wave_functions]

    def oscillators(self, wave_functions, octave, duration, sample_rate):
        return self._oscillators(self, octave, wave_functions, duration, sample_rate)

    @staticmethod
    def mix_samples(samples):
        return np.sum(samples, axis=0)


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
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.pyaudio_stream().stop_stream()
        self.pyaudio_stream().close()
        self.pyaudio_stream.cache_clear()

    def play(self, samples):
        self.pyaudio_stream().write(samples)


# a synthesizer that plays notes from octave 0 to octave 10 for every note sorted by frequency when keys are pressed
class Synthesizer:
    def __init__(self):
        self.keys = {}
        for octave in range(0, 11):
            for note in Note:
                self.keys[f"{note.name}{octave}"] = partial(note.wave, octave)

    def play(self, key, wave, duration, sample_rate):
        with AudioStream() as audio_stream:
            audio_stream.play(self.keys[key](wave, duration, sample_rate))


    # use the keyboard module to map keys to notes and then create a synthesizer that plays the notes
    def keyboard_synthesizer(self):
        while True:
            if keyboard.is_pressed('1'):
                self.play('C4', 'sine', 0.5, 44100)
            if keyboard.is_pressed('2'):
                self.play('D4', 'sine', 0.5, 44100)
            if keyboard.is_pressed('3'):
                self.play('E4', 'sine', 0.5, 44100)
            if keyboard.is_pressed('4'):
                self.play('F4', 'sine', 0.5, 44100)
            if keyboard.is_pressed('5'):
                self.play('G4', 'sine', 0.5, 44100)
            if keyboard.is_pressed('6'):
                self.play('A4', 'sine', 0.5, 44100)
            if keyboard.is_pressed('7'):
                self.play('B4', 'sine', 0.5, 44100)
            if keyboard.is_pressed('8'):
                self.play('C5', 'sine', 0.5, 44100)
            if keyboard.is_pressed('9'):
                self.play('D5', 'sine', 0.5, 44100)
            if keyboard.is_pressed('0'):
                self.play('E5', 'sine', 0.5, 44100)
            if keyboard.is_pressed('q'):
                self.play('C4', 'sine', 0.5, 44100)
            if keyboard.is_pressed('w'):
                self.play('D4', 'sine', 0.5, 44100)



if __name__ == "__main__":
   Synthesizer().keyboard_synthesizer()





