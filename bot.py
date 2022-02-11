import asyncio
import os

import youtube_dl
import sys, os
import json, requests

import aiohttp
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.exceptions import AlreadyJoinedError
from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types import Update
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import InputStream
import conf
app = Client(
    'py-tgcalls',
    api_id=os.environ.get("API_ID"),
    api_hash=os.environ.get("API_HASH"),
)
call_py = PyTgCalls(app)

def parse_command(prefix, text):
    if text[:1] == prefix:
        rm_prefix = text[1:].split(' ')
        if len(rm_prefix) != 1:
            commands = rm_prefix[0]
            value = text[1:].split(' ', 1)[1]
            return {
                'value' : value,
                'command' : commands,
                'error' : None
            }
        else:
            commands = rm_prefix[0]
            # value = text[1:].split(' ', 1)[1]
            return {
                'value' : None,
                'command' : commands,
            'error' : None
            }

    else:
        return {
            'value' : None,
            'command' : None,
            'error' : "PREFIX_NDAK_VALID"
        }

# listradio = {
#     "rodja":"https://radioislamindonesia.com/rodja.mp3",
#     "aliman":"https://radioislamindonesia.com/aliman.mp3",
#     "mutiaraquran":"https://radioislamindonesia.com/mutiaraquran.mp3",
#     "mutiaraquran":"https://radioislamindonesia.com/mutiaraquran.mp3",
#     "radiomadinah":"http://radioislamindonesia.com/radiomadinah.mp3",
#     "rodja-bandung":"http://radioislamindonesia.com/rodja-bandung.mp3",
#     "rodja-low":"http://radioislamindonesia.com/rodja-low.mp3",
#     "shahabatmuslim":"http://radioislamindonesia.com/shahabatmuslim.mp3",
#     "tarbiyah":"http://radioislamindonesia.com/tarbiyah.mp3",
#     "andikafm":"http://stream2.andikafm.com:1057/andikafm",
#     "geronimo_jogja":"http://live2.indostreamserver.com:8018/stream?type=http&amp;nocache=47704",
#     "global_radio":"http://202.147.199.98/;stream.nsv",
#     "kompas_sonora_jakarta":"http://103.226.246.245/kompas-sonorajakarta",
#     "qz_radio_bandung":"http://45.64.97.211:1031/;stream.nsv",
#     "radio_muslim":"http://live.radiomuslim.com/;stream/1/;",
#     "radio_muslim_mirror2":"https://cp.phpmystream.com/radioSSLnew/s/75;",
    
#     "rama_fm_bandung":"http://rama-fm.simaya.net.id:8800/stream?type=http&nocache=260",
#     "sindo_trijaya_fm":"http://202.147.199.101:8000/;?type=http&nocache=16993",
#     "elshinta_jakarta":"https://stream-ssl.arenastreaming.com:8000/jakarta",
#     "trax_fm_jakarta":"https://n02.radiojar.com/rrqf78p3bnzuv.mp3?rj-ttl=5&rj-tok=AAABfuEWysMADAqTqKFWPFr6ng",
#     "trax_fm_semarang":"http://n06.radiojar.com/fr9zqhv80k8uv?rj-ttl=5&rj-tok=AAABfuEaXtUAZdo9aZTRY83-zg",
#     "trax_fm_palembang":"n07.radiojar.com/qv4muvhswk8uv?rj-ttl=5&rj-tok=AAABfuEbsiEAlfcGz-RDo94j9Q",
#     "":"",
#     "":"",
#     "":"",
#     "":"",
#     "":"",
#     "":"",
    
# }

@app.on_message()
async def play_handler(client: Client, message: Message):
    rettc = parse_command("/", message.text)
    if rettc["error"] == 'PREFIX_NDAK_VALID':
        pass
    else:
        
        if rettc["command"] == "play":
            if rettc["value"] == None:
                msg = 'Maaf, gunakan /play {nama radio}\n\nSelengkapnya sila liat command /radio'
                await client.send_message(
                    message.chat.id, str(msg),reply_to_message_id=message.message_id
                )
            else:
                listradio = json.loads(requests.get("https://api.npoint.io/4fbda314fb8cae63b507").text)
                try:
                    hostradio = listradio[rettc["value"]]
                except KeyError:
                    msg = 'Maaf, radio tdk ditemukan\n\nSelengkapnya sila liat command /radio'
                    await client.send_message(
                        message.chat.id, str(msg),reply_to_message_id=message.message_id
                    )
                    hostradio = False
                if hostradio != False:
                    
                    try:
                        msg = "Silahkan tunggu hingga radio berbunyi, Jika sudah 40 detik radio belum juga berbunyi, berati ada error di sistem"
                        await client.send_message(
                            message.chat.id, str(msg),reply_to_message_id=message.message_id
                        )
                        print("streaming : " + hostradio)
                        await call_py.join_group_call(
                            message.chat.id,
                            AudioPiped(
                                hostradio,
                                # HighQualityAudio(),
                                # HighQualityVideo(),
                            ),
                            stream_type=StreamType().pulse_stream,
                        )
                        msg = 'Berhasil, bot sedang streaming radio ' + rettc["value"]
                        await client.send_message(
                            message.chat.id, str(msg),reply_to_message_id=message.message_id
                        )
                    except asyncio.exceptions.TimeoutError:
                        msg = 'tidak dapat streaming radio ini, Exception by asyncio.exceptions.TimeoutError'
                        await client.send_message(
                            message.chat.id, str(msg),reply_to_message_id=message.message_id
                        )
                    except AlreadyJoinedError:
                        await call_py.change_stream(
                            message.chat.id,
                            AudioPiped(
                                hostradio,
                                # HighQualityAudio(),
                                # HighQualityVideo(),
                            )
                            #stream_type=StreamType().pulse_stream
                        )
                        msg = 'Berhasil, stream dirubah ke radio ' + rettc["value"]
                        await client.send_message(
                            message.chat.id, str(msg),reply_to_message_id=message.message_id
                        )
                    except aiohttp.client_exceptions.ServerDisconnectedError:
                        msg = "Error, terputus dari server, Exception by aiohttp.client_exceptions.ServerDisconnectedError"
                        await client.send_message(
                            message.chat.id, str(msg),reply_to_message_id=message.message_id
                        )
                    except aiohttp.client_exceptions.ClientResponseError:
                        msg = "Error, Klien mendapat respon error dari server, Exception by aiohttp.client_exceptions.ClientResponseError"
                        await client.send_message(
                            message.chat.id, str(msg),reply_to_message_id=message.message_id
                        )
                    except FileNotFoundError:
                        msg = "Error, Klien tidak dapat menemukan server. Exception by FileNotFoundError"
                        await client.send_message(
                            message.chat.id, str(msg),reply_to_message_id=message.message_id
                        )
        elif rettc["command"] == "radio":
            listradio = json.loads(requests.get("https://api.npoint.io/4fbda314fb8cae63b507").text)
            
            if rettc["value"] != None:
                try:
                    page = int(rettc["value"])
                    valerr = False
                except ValueError:
                    msg = "Inputan salah!, input harus angka untuk berpindah halaman, contoh /radio 2"
                    await client.send_message(
                        message.chat.id, str(msg),reply_to_message_id=message.message_id
                    )
                    valerr = True
                if valerr == False:
                    perpage = 10
                    initial = 0
                    initkosong = ''
                    key = list(listradio.keys())

                    for a in range(perpage * page - 10, perpage * page):

                        try:
                            keysrad = key[a]
                            initkosong = initkosong + f"{a + 1}. ```{keysrad}```\n"
                        except IndexError:
                            keysrad = initkosong + ""
                    msg = "daftar isi radio\n\n" + initkosong + "\n\nUtk berpindah halaman, gunakan /radio {nomor halaman}\nContoh: ```/radio 2```\n\nUtk memainkan radio, gunakan /play {nama radio di daftar tsb}"
                    await client.send_message(
                        message.chat.id, str(msg),reply_to_message_id=message.message_id
                    )
            else:
                page = 1
                perpage = 10
                initial = 0
                initkosong = ''
                key = list(listradio.keys())

                for a in range(perpage * page - 10, perpage * page):

                    try:
                        keysrad = key[a]
                        initkosong = initkosong + f"{a + 1}. ```{keysrad}```\n"
                    except IndexError:
                        keysrad = initkosong + ""
                msg = "daftar isi radio\n\n" + initkosong + "\n\nUtk berpindah halaman, gunakan /radio {nomor halaman}\nContoh: ```/radio 2```\n\nUtk memainkan radio, gunakan /play {nama radio di daftar tsb}"
                await client.send_message(
                    message.chat.id, str(msg),reply_to_message_id=message.message_id
                )
        elif rettc["command"] == "pause":
            msg = 'Radio diberhentikan'
            await client.send_message(
                message.chat.id, str(msg),reply_to_message_id=message.message_id
            )
            await call_py.pause_stream(
                message.chat.id,
            )
        elif rettc["command"] == "resume":
            msg = 'Radio dilanjutkan'
            await client.send_message(
                message.chat.id, str(msg),reply_to_message_id=message.message_id
            )
            await call_py.resume_stream(
                message.chat.id,
            )
        elif rettc["command"] == "stop":
            msg = 'Radio berhenti, bot keluar dari voice call'
            await client.send_message(
                message.chat.id, str(msg),reply_to_message_id=message.message_id
            )
            await call_py.leave_group_call(
                message.chat.id,
            )

@call_py.on_kicked()
async def kicked_handler(client: PyTgCalls, chat_id: int):
    print(f'Kicked from {chat_id}')


@call_py.on_raw_update()
async def raw_handler(client: PyTgCalls, update: Update):
    print(update)


@call_py.on_stream_end()
async def stream_end_handler(client: PyTgCalls, update: Update):
    print(f'Stream ended in {update.chat_id}', update)


@call_py.on_participants_change()
async def participant_handler(client: PyTgCalls, update: Update):
    print(update)

call_py.start()
idle()
