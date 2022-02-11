
import sys


import asyncio
import sys, os

from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types import Update
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import InputStream
import conf
from pytgcalls.types import Browsers
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.types.input_stream.quality import HighQualityVideo

app = Client(
    'py-tgcalls',
    api_id=os.environ.get("API_ID"),
    api_hash=os.environ.get("API_HASH"),
)
call_py = PyTgCalls(app)
call_py.start()
# target = int(input("targetid : "))
# while True:
call_py.join_group_call(
    #-1001182246595 cscript
    -1001410961692, 
      AudioPiped(
        input("radio : "),
        # HighQualityAudio(),
        # HighQualityVideo(),
        
        headers={
            'User-Agent': Browsers().chrome_windows,
        }
    ),
    stream_type=StreamType().live_stream,
)

idle()
