#!/usr/bin/env python3
# from punctuator import Punctuator
import asyncio
import concurrent.futures
import json
import os
import queue
import ssl
import struct
import threading
import wave
from pathlib import Path
from sys import platform

import aiohttp_cors
import numpy
import socketio
from aiohttp import WSMsgType, web

# from av.audio.resampler import AudioResampler
from engineio.payload import Payload
from furl import furl

# from asr_engines import init_download

# init_download()

Payload.max_decode_packets = 16384
ROOT = Path(__file__).parent

sample_rate = 16000

vosk_interface = os.environ.get("VOSK_SERVER_INTERFACE", "localhost")
vosk_port = int(os.environ.get("VOSK_SERVER_PORT", 8888))
vosk_cert_file = os.environ.get("VOSK_CERT_FILE", None)
vosk_key_file = os.environ.get("VOSK_KEY_FILE", None)
vosk_cert_file = os.environ.get(
    "VOSK_CERT_FILE", "/etc/letsencrypt/live/teacher.mylanguage.me/cert.pem"
)
vosk_key_file = os.environ.get(
    "VOSK_KEY_FILE", "/etc/letsencrypt/live/teacher.mylanguage.me/privkey.pem"
)
# p = Punctuator('./Demo-Europarl-EN.pcl')

pool = concurrent.futures.ThreadPoolExecutor((os.cpu_count() or 1))
loop = asyncio.get_event_loop()

# sio = socketio.AsyncServer(cors_allowed_origins=[])
sio = socketio.AsyncServer(cors_allowed_origins="*")
clients = {}
record_idx = 0
wav_data = []
is_record = False
# provider
au_provider = ""
import time


@sio.on("message")
def onmessage(sid, message):
    stream_task = clients[sid]
    if stream_task is not None:
        stream_task.process(message)
    # await kaldi.run_audio_xfer()


@sio.on("auprovider")
def onauprovider(sid, au_type):
    stream_task = clients[sid]
    stream_task.au_provider = au_type
    print("audio provider : ", stream_task.au_provider)
    stream_task.start()


@sio.event
def connect(sid, environ):
    start_record_info()

    print("connect", sid)
    stream_task = ASRStreamTask(sid)
    # sio.send("Hello", sid)
    clients[sid] = stream_task
    stream_task.start()


@sio.event
def disconnect(sid):
    print("disconnect", sid)
    reset_record_info()
    clients[sid].stop()
    clients[sid] = None


def reset_record_info():
    global is_record
    is_record = False


def start_record_info():
    global is_record, wav_data
    wav_data = []
    is_record = True


def record_audio(audio_data):
    global is_record, wav_data
    if is_record:
        wav_data.append(audio_data)


def save_wav_data(wav_path):
    global wav_data, sample_rate
    if len(wav_data) > 0:
        all_data = numpy.concatenate(wav_data, axis=None)
        # raw_ints = struct.pack("<%dh" % len(all_data), *all_data)
        # raw_ints = struct.pack("<%dh" % len(all_data[0]), *all_data[0])

        # print(all_data)
        wf = wave.open(wav_path, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(all_data)
        wf.close()
        return wav_path
    else:
        return ""


def process_chunk(rec, message):
    if rec.AcceptWaveform(message):
        return rec.Result()
    else:
        return rec.PartialResult()


def transcribe_audio(stream_task):
    stream_task.run_audio_xfer()


class ASRStreamTask:
    def __init__(self, socket_id):
        # self.__resampler = AudioResampler(format='s16', layout='mono', rate=sample_rate)
        self.__sid = socket_id
        self.__audio_task = None

        self.au_provider = ""

        self.is_stop = False
        self.frame_queue = queue.Queue(maxsize=100)
        self.result_queue = queue.Queue(maxsize=100)
        self.prev_send_time = 0

    # async def start(self):
    def start(self):
        self.is_stop = False
        self.__audio_task = threading.Thread(
            name="transcribe thread" + str(self.__sid),
            target=transcribe_audio,
            args=(clients[self.__sid],),
        )
        self.__audio_task.start()

    # async def stop(self):
    def stop(self):
        if self.__audio_task is not None:
            # self.__audio_task.cancel()
            self.is_stop = True
            self.__audio_task.join()
            self.__audio_task = None

    async def _add(self, frame):
        self.frame_queue.put(frame)
        cur_time = time.time()
        if self.result_queue.qsize() > 0:
            response = self.result_queue.get()
            print("Sending response", response, self.__sid)
            try:
                await sio.send(response, self.__sid)
                self.prev_send_time = cur_time
            except KeyError:
                pass
        elif cur_time - self.prev_send_time > 0.2:
            response = json.dumps({"partial": ""})
            print("Sending response", response, self.__sid)
            try:
                await sio.send(response, self.__sid)
                self.prev_send_time = cur_time
            except KeyError:
                pass

    def process(self, frame):
        loop.create_task(self._add(frame))

    def _get_asr_engine(self, provider):
        # {'flag': 'ES', 'langcode': 'ca-ES', 'country_name': 'Catalan (Spain)', 'provider': "google"}
        # google , microsoft, wav2vec, whisper, vosk
        from asr_engines import AzureEngine, language_code

        asr_engine = AzureEngine(language_code)

        return asr_engine

    def run_audio_xfer(self):
        idx = 0
        prev_str = ""
        response = ""
        is_first_final = True
        asr_engine = self._get_asr_engine(self.au_provider)
        while True:
            if self.is_stop:
                print("Sending response", response, self.__sid)
                self.result_queue.put(response)
                break

            if self.frame_queue.empty():
                time.sleep(0.01)
                continue

            frame = self.frame_queue.get()
            # record frame
            record_audio(frame)

            # get speech to text result
            if asr_engine is not None:
                response = asr_engine.get_transcription(frame)
                # response = await loop.run_in_executor(pool, process_chunk, self.__recognizer, frame.tobytes())
                idx += 1
                res_dict = json.loads(response)
                if "partial" in res_dict:
                    if len(res_dict["partial"]) > 0 or idx < 2:
                        if len(prev_str) > 0 and prev_str == res_dict["partial"]:
                            continue
                        prev_str = res_dict["partial"]
                    else:
                        continue
                else:
                    if "text" not in res_dict:
                        continue

                    if len(res_dict["text"].strip()) == 0:
                        continue

                    if len(res_dict["text"]) > 0:
                        if is_first_final:
                            res_dict["text"] = "{}{}".format(
                                res_dict["text"][0].upper(), res_dict["text"][1:]
                            )
                            # is_first_final = False
                        # res_dict["text"]=p.punctuate(res_dict["text"])
                        response = json.dumps(res_dict)

                print("Adding response", response)
                self.result_queue.put(response)


async def index(request):
    content = open(str(ROOT / "static" / "index.html")).read()
    return web.Response(content_type="text/html", text=content)


async def get_wav_path(request):
    reset_record_info()
    params = furl(request.path_qs)

    if platform == "win32":
        wav_file_path = "E:/xampp/htdocs/langs/public/audio/{}".format(
            params.args["fname"]
        )
    else:
        wav_file_path = "/var/www/html/public/audio/{}".format(params.args["fname"])

    wav_path = save_wav_data(wav_file_path)
    if len(wav_path) == 0:
        wav_path = "invalid_data"
    return web.Response(content_type="text/html", text=wav_path)


if __name__ == "__main__":
    # if platform != "win32":
    #     ssl_context = ssl.SSLContext()
    #     ssl_context.load_cert_chain(vosk_cert_file, vosk_key_file)
    # else:
    ssl_context = None

    app = web.Application()
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )

    cors.add(app.router.add_route("GET", "/", index))
    # app.router.add_route('GET', '/', index)
    app.router.add_static("/static/", path=ROOT / "static", name="static")
    cors.add(app.router.add_route("GET", "/wav_path", get_wav_path))
    # app.router.add_route('GET', '/wav_path', get_wav_path)

    # app.config['CORS_AUTOMATIC_OPTIONS'] = True
    # app.config['CORS_SUPPORTS_CREDENTIALS'] = True
    sio.attach(app)
    # CORS(app)
    # @cross_origin(app)
    # @authorized()
    web.run_app(app, port=vosk_port)
