import json
import os
import concurrent.futures
import asyncio
import numpy
import wave
import queue
from pathlib import Path
from sys import platform
import threading, time
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import urlparse
import socketio
from asr_engines import AzureEngine

ROOT = Path(__file__).parent

sample_rate = 16000

app = FastAPI()
clients = {}
record_idx = 0
wav_data = []
is_record = False


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    sid = websocket._connection_id

    start_record_info()
    stream_task = ASRStreamTask(sid)

    clients[sid] = stream_task
    stream_task.start()

    while True:
        try:
            message = await websocket.receive_text()
            stream_task.process(message)
        except Exception as e:
            break

    reset_record_info()
    stream_task.stop()
    clients.pop(sid, None)
    await websocket.close()


async def index(request: Request):
    content = open(str(ROOT / "static" / "index.html")).read()
    return HTMLResponse(content=content)


async def get_wav_path(request: Request):
    reset_record_info()
    params = dict(urlparse(request.url).query)

    if platform == "win32":
        wav_file_path = "E:/xampp/htdocs/langs/public/audio/{}".format(params["fname"])
    else:
        wav_file_path = "/var/www/html/public/audio/{}".format(params["fname"])

    wav_path = save_wav_data(wav_file_path)
    if len(wav_path) == 0:
        wav_path = "invalid_data"
    return wav_path


app.add_websocket_route("/", websocket_endpoint)
app.add_route("/", index)
app.add_route("/wav_path", get_wav_path)
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


sample_rate = 16000

pool = concurrent.futures.ThreadPoolExecutor((os.cpu_count() or 1))
loop = asyncio.get_event_loop()

clients = {}
record_idx = 0
wav_data = []
is_record = False

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


class ASRStreamTask:
    def __init__(self, socket_id):
        self.__sid = socket_id
        self.__audio_task = None

        self.au_provider = ""

        self.is_stop = False
        self.frame_queue = queue.Queue(maxsize=100)
        self.result_queue = queue.Queue(maxsize=100)
        self.prev_send_time = 0

    def start(self):
        self.is_stop = False
        self.__audio_task = threading.Thread(
            name="transcribe thread" + str(self.__sid),
            target=AzureEngine.get_transcription(),
            args=(clients[self.__sid],),
        )
        self.__audio_task.start()

    def stop(self):
        if self.__audio_task is not None:
            self.is_stop = True
            self.__audio_task.join()
            self.__audio_task = None

    def process(self, frame):
        loop.create_task(self._add(frame))

    async def _add(self, frame):
        self.frame_queue.put(frame)
        cur_time = time.time()
        if self.result_queue.qsize() > 0:
            response = self.result_queue.get()
            try:
                await sio.send(response, self.__sid)
                self.prev_send_time = cur_time
            except KeyError:
                pass
        elif cur_time - self.prev_send_time > 0.2:
            response = json.dumps({"partial": ""})
            try:
                await sio.send(response, self.__sid)
                self.prev_send_time = cur_time
            except KeyError:
                pass

    def run_audio_xfer(self):
        idx = 0
        prev_str = ""
        response = ""
        is_first_final = True
        asr_engine = self._get_asr_engine(self.au_provider)
        while True:
            if self.is_stop:
                self.result_queue.put(response)
                break

            if self.frame_queue.empty():
                time.sleep(0.01)
                continue

            frame = self.frame_queue.get()
            record_audio(frame)

            if asr_engine is not None:
                response = asr_engine.get_transcription(frame)
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
                        response = json.dumps(res_dict)

                self.result_queue.put(response)


def start_record_info():
    global is_record, wav_data
    wav_data = []
    is_record = True


def reset_record_info():
    global is_record
    is_record = False


def record_audio(audio_data):
    global is_record, wav_data
    if is_record:
        wav_data.append(audio_data)


def save_wav_data(wav_path):
    global wav_data, sample_rate
    if len(wav_data) > 0:
        all_data = numpy.concatenate(wav_data, axis=None)
        wf = wave.open(wav_path, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(all_data)
        wf.close()
        return wav_path
    else:
        return ""


if __name__ == "__main__":
    import uvicorn

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8000"
        ],  # Replace with the origin of your client code
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
    )
