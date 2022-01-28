import functools
import logging
import time

import pyaudio
import wave
import asyncio
from typing import Dict, Optional, List, Union, Pattern, Callable, Coroutine, Any

RecordHandler = Callable[..., Coroutine]
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5


class RAudioReq:
    name: str
    dir: str
    handler: Coroutine

    def __init__(self, name: str, handler: RecordHandler, dir: str):
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError("RAudioReq handler must be coroutine")
        self.handler = handler
        self.name = name or handler.__name__
        self.dir = dir
        if not isinstance(self.name, str):
            raise TypeError("Name of a Command must be a String")

    @staticmethod
    def req(name: str = '', dir: str = ''):
        def deco(handler: RecordHandler):
            return RAudioReq(name, handler, dir)

        return deco


class RecordManager:
    handler_map = {}
    path: str

    def __init__(self):
        print('deco init')
        self.handler_map = {}
        self.append_funcs = []

    def __getitem__(self, item):
        print(f'get item: {item}')
        print(f'handler_map : {self.handler_map}')
        return self.handler_map.get(item, None)

    def __setitem__(self, key: str, value: RAudioReq):
        print(f'set item: {key}')
        self.handler_map[key] = value

    def __call__(self, *args, **kwargs):
        print(f'deco begin : {kwargs}')
        return lambda func: self.add('res/result', kwargs['play'], kwargs['complete'], func)

    def add(self, path: str, play: bool, complete: bool, func: Callable):
        print(f'deco added:{path}')
        if play:
            self[path + '_play' + ('_begin' if not complete else '_end')] = func
        else:
            self[path + '_record' + ('_begin' if not complete else '_end')] = func


class Recorder:
    is_running: bool
    regist: RecordManager
    loop: asyncio.AbstractEventLoop
    queue: asyncio.Queue
    audio: pyaudio.PyAudio
    record_stream: pyaudio.Stream
    is_recording: bool

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()
        self.audio = pyaudio.PyAudio()
        self.is_running = False
        self.regist = RecordManager()
        self.is_recording = False

    def regist_func(self, path, func):
        self.regist[path] = func

    async def start(self):
        if self.is_running:
            raise RuntimeError('recorder is running')
        self.is_running = True

        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ",
                      self.audio.get_device_info_by_host_api_device_index(0, i).get('name'))

    def run(self):
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            logging.info('next')

    audio_frames: List[Any] = []

    def record_stream_callback(self, in_data, frame_count, time_info, status):
        print(f'.{time_info}')
        self.audio_frames.append(in_data)
        return b"", pyaudio.paContinue

    async def _record(self, path: str = 'res/result'):
        self.is_recording = True
        p = self.audio  # Create an interface to PortAudio
        print('Recording')
        self.record_stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        frames_per_buffer=CHUNK,
                        input=True,
                        stream_callback=self.record_stream_callback)
        self.record_stream.start_stream()
        await self.regist['res/result_record_begin'](path)

    async def end_record(self, path: str):
        self.is_recording = False
        file_name = path
        self.record_stream.stop_stream()
        self.record_stream.close()
        print('Finished recording')
        with wave.open(file_name, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.audio_frames))
            self.audio_frames = []

        await self.regist['res/result_record_end'](path)

    def beginrec(self, file_name: str):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._record(file_name))

    def stoprec(self, file_name: str):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.end_record(file_name))

    def beginplay(self, file_name: str):
        wav = wave.open(file_name)
        wav_data = wav.readframes(wav.getnframes())
        audio = self.audio
        stream_out = audio.open(
            format=audio.get_format_from_width(wav.getsampwidth()),
            channels=wav.getnchannels(),
            rate=wav.getframerate(),
            input=False,
            output=True
        )
        stream_out.start_stream()
        stream_out.write(wav_data)
        # time.sleep(0.2)
        stream_out.stop_stream()
        stream_out.close()

    def play(self, *args):
        print('set play1')

        def wrapper(*args, **kwargs):
            print('wrap play')
            func = args[0]

            async def _play(path: str):
                print('run play')
                file_name = path + 'test.wav'
                wav = wave.open(file_name)
                wav_data = wav.readframes(wav.getnframes())
                audio = pyaudio.PyAudio()
                stream_out = audio.open(
                    format=audio.get_format_from_width(wav.getsampwidth()),
                    channels=wav.getnchannels(),
                    rate=wav.getframerate(),
                    input=False,
                    output=True
                )
                stream_out.start_stream()
                stream_out.write(wav_data)
                # time.sleep(0.2)
                stream_out.stop_stream()
                stream_out.close()
                audio.terminate()
                print('play complete')
                return await func(path)
            return _play
        return wrapper
