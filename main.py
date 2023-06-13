import asyncio
import os
from typing import AsyncIterable, Awaitable

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import BaseModel

load_dotenv()

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = ""

app = FastAPI()
path = ""


async def send_message(message: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    model = ChatOpenAI(
        streaming=True,
        verbose=True,
        callbacks=[callback],
    )

    async def wrap_done(fn: Awaitable, event: asyncio.Event):
        """Wrap an awaitable with an event to signal when it's done or an exception is raised."""
        try:
            await fn
        except Exception as e:
            print(f"Caught exception: {e}")
        finally:
            event.set()

    if path == "/generate_clinical_history":
        initial_prompt = initial_prompt_for_clinical_history
    elif path == "/generate_differential_diagnosis":
        initial_prompt = initial_prompt_for_differential_diagnosis
    elif path == "/generate_tcm_advice":
        initial_prompt = initial_prompt_for_tcm_advice
    else:
        initial_prompt = "Not a valid endpoint"

    initial_messages = [
        [HumanMessage(content=initial_prompt)],
        [HumanMessage(content=message)],
    ]

    task = asyncio.create_task(
        wrap_done(model.agenerate(messages=initial_messages), callback.done),
    )

    async for token in callback.aiter():
        yield f"data: {token}\n\n"

    await task


class SummaryInput(BaseModel):
    message: str


initial_prompt_for_clinical_history = "你是一個中醫師助理，請將以下內容轉變成病史。 切記內容要準確，不可以擅自增添內容，用字要用標準的病史寫法，要用繁體字：列表 入院前兩日唔小心受涼有咽喉痛、鼻塞陣發性非刺激性咳嗽，較劇烈黃綠色痰，量少，難咳出輕度畏寒 全身酸痛唔舒服 - 冇寒顫、高燥、頭暈、心跳加速 - 冇腹痛腹瀉 - 未經任何處理 - 之前無好轉，來求診並入院 病史： 主訴:咽痛鼻塞咳嗽2天 現病史：入院前2天不慎受涼後,出現咽痛、鼻塞,繼而出現咳嗽,呈陣發性非刺激性,較劇烈,痰呈黃綠色,量少,難咳出,並感輕度畏寒,全身酸痛不適,無寒戰高熱,無頭暈頭痛,無胸悶心悸,無腹痛腹瀉等,未予注意,未經任何處理,經休息上述病情無好轉,今求診我院; 列表 上腹部脹痛兩日 - 飲食不節後出現病症 - 持續痛楚，飯後更甚 - 不想進食 - 有時感到噁心想嘔 - 沒有畏寒發燒 - 沒有頭暈頭痛 - 沒有胸悶心悸 - 沒有腹瀉黑便等 - 曾到當地診所就診 - 服藥後未見改善，遂來本院 病史： 主訴:上腹脹痛2天 現病史：入院前2天飲食不節後,出現上腹脹痛,呈持續性,餐後尤甚,致不思飲食,時有噁心欲"
initial_prompt_for_differential_diagnosis = "你是一個中醫師助理，請將以下內容轉變成病史。 切記內容要準確，不可以擅自增添內容，用字要用標準的病史寫法，要用繁體字：列表 入院前兩日唔小心受涼有咽喉痛、鼻塞陣發性非刺激性咳嗽，較劇烈黃綠色痰，量少，難咳出輕度畏寒 全身酸痛唔舒服 - 冇寒顫、高燥、頭暈、心跳加速 - 冇腹痛腹瀉 - 未經任何處理 - 之前無好轉，來求診並入院 病史： 主訴:咽痛鼻塞咳嗽2天 現病史：入院前2天不慎受涼後,出現咽痛、鼻塞,繼而出現咳嗽,呈陣發性非刺激性,較劇烈,痰呈黃綠色,量少,難咳出,並感輕度畏寒,全身酸痛不適,無寒戰高熱,無頭暈頭痛,無胸悶心悸,無腹痛腹瀉等,未予注意,未經任何處理,經休息上述病情無好轉,今求診我院; 列表 上腹部脹痛兩日 - 飲食不節後出現病症 - 持續痛楚，飯後更甚 - 不想進食 - 有時感到噁心想嘔 - 沒有畏寒發燒 - 沒有頭暈頭痛 - 沒有胸悶心悸 - 沒有腹瀉黑便等 - 曾到當地診所就診 - 服藥後未見改善，遂來本院 病史： 主訴:上腹脹痛2天 現病史：入院前2天飲食不節後,出現上腹脹痛,呈持續性,餐後尤甚,致不思飲食,時有噁心欲"
initial_prompt_for_tcm_advice = "你是一個中醫師助理，請將以下內容轉變成病史。 切記內容要準確，不可以擅自增添內容，用字要用標準的病史寫法，要用繁體字：列表 入院前兩日唔小心受涼有咽喉痛、鼻塞陣發性非刺激性咳嗽，較劇烈黃綠色痰，量少，難咳出輕度畏寒 全身酸痛唔舒服 - 冇寒顫、高燥、頭暈、心跳加速 - 冇腹痛腹瀉 - 未經任何處理 - 之前無好轉，來求診並入院 病史： 主訴:咽痛鼻塞咳嗽2天 現病史：入院前2天不慎受涼後,出現咽痛、鼻塞,繼而出現咳嗽,呈陣發性非刺激性,較劇烈,痰呈黃綠色,量少,難咳出,並感輕度畏寒,全身酸痛不適,無寒戰高熱,無頭暈頭痛,無胸悶心悸,無腹痛腹瀉等,未予注意,未經任何處理,經休息上述病情無好轉,今求診我院; 列表 上腹部脹痛兩日 - 飲食不節後出現病症 - 持續痛楚，飯後更甚 - 不想進食 - 有時感到噁心想嘔 - 沒有畏寒發燒 - 沒有頭暈頭痛 - 沒有胸悶心悸 - 沒有腹瀉黑便等 - 曾到當地診所就診 - 服藥後未見改善，遂來本院 病史： 主訴:上腹脹痛2天 現病史：入院前2天飲食不節後,出現上腹脹痛,呈持續性,餐後尤甚,致不思飲食,時有噁心欲"


@app.post("/generate_clinical_history")
def stream(body: SummaryInput):
    global path
    path = "/generate_tcm_advice"
    return StreamingResponse(send_message(body.message), media_type="text/event-stream")


@app.post("/generate_differential_diagnosis")
def stream(body: SummaryInput):
    global path
    path = "/generate_tcm_advice"
    return StreamingResponse(send_message(body.message), media_type="text/event-stream")


@app.post("/generate_tcm_advice")
def stream(body: SummaryInput):
    global path
    path = "/generate_tcm_advice"
    return StreamingResponse(send_message(body.message), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(host="0.0.0.0", port=8000, app=app)
