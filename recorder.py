import pyaudio
import asyncio
from typing import Dict, Optional, List, Union, Pattern, Callable, Coroutine, Any

RecordHandler = Callable[..., Coroutine]

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
            raise  TypeError("Name of a Command must be a String")





class Recorder:
    _cmd_map: Dict[str, RAudioReq]

    def record(self):
        def _record(method: str, **kwargs):
            pass
        return _record

    def play(self):
        pass
