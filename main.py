import json
import os

import openai
import uvicorn
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import StreamingResponse

_ = load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


class SummaryInput(BaseModel):
    summary: str


def generate_clinical_history(summary: str) -> str:
    initial_prompt = "你是一個中醫師助理，請將以下內容轉變成病史。 切記內容要準確，不可以擅自增添內容，用字要用標準的病史寫法，要用繁體字：\n————————————\n列表：\n- 入院前兩日唔小心受涼\n- 有咽喉痛、鼻塞\n- 陣發性非刺激性咳嗽，較劇烈\n- 黃綠色痰，量少，難咳出\n- 輕度畏寒\n- 全身酸痛唔舒服\n- 冇寒顫、高燥、頭暈、心跳加速\n- 冇腹痛腹瀉\n- 未經任何處理\n- 之前無好轉，來求診並入院\n病史：\n主訴:咽痛鼻塞咳嗽2天\n現病史：入院前2天不慎受涼後,出現咽痛、鼻塞,繼而出現咳嗽,呈陣發性非刺激性,較劇烈,痰呈黃綠色,量少,難咯,並感輕度畏寒,全身酸痛不適,無寒戰高熱,無頭暈頭痛,無胸悶心悸,無腹痛腹瀉等,未予注意,未經任何處理,經休息上述病情無好轉,今求診我院;\n——————————————\n列表：\n- 上腹部脹痛兩日\n- 飲食不節後出現病症\n- 持續痛楚，飯後更甚\n- 不想進食\n- 有時感到噁心想嘔\n- 沒有畏寒發燒\n- 沒有頭暈頭痛\n- 沒有胸悶心悸\n- 沒有腹瀉黑便等\n- 曾到當地診所就診\n- 服藥後未見改善，遂來本院\n病史：\n主訴:上腹脹痛2天\n現病史：入院前2天飲食不節後,出現上腹脹痛,呈持續性,餐後尤甚,致不思飲食,時有噁心欲吐,無畏冷發熱,無頭暈頭痛,無胸悶心悸,無腹瀉黑便等,就診於當地診所,予“藥物口服” 具體用藥欠祥,上述病情無好轉,今求診我院;\n————————————————\n列表：\n- 上腹脹痛兩日\n- 食物不潔感覺\n- 臍周痛，持續性\n- 腹瀉黃水樣，粘液，每日超過10次\n- 洩瀉後腹痛稍緩解\n- 肛門灼熱感\n- 時有噁心嘔吐\n- 無畏冷發熱\n- 無眩暈頭痛\n- 無胸悶心悸\n- 無黑便\n- 曾就醫並服藥，但具體情況未知\n- 病情有改善，就診本院\n病史：\n主訴:上腹脹痛2天\n現病史：入院前2天飲食不潔後,出現腹痛,以臍周為主,呈持續性隱痛,陣發性加劇,同時出現腹瀉,呈黃色浠水樣,夾有粘液,日10餘次,洩後腹痛稍緩解,伴肛門灼熱感,時有噁心欲吐,無畏冷發熱,無頭暈頭痛,無胸悶心悸,無黑便等,就診於當地診所,予“藥物口服” 具體用藥欠祥,上述病情稍好轉,今求診我院;"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": summary},
        ],
        temperature=0,
    )
    return response.choices[0].message


def generate_differential_diagnosis(summary: str) -> str:
    initial_prompt = "你是一個家庭醫學專家，請使用你的知識，輔助基層中醫，讓他們提供更全面的診療思路。\n\n請參考病例重點， 提出疾病初步診斷以及鑒別診斷以及鑒別診斷所需的資訊或檢查\n\n請以以下方式輸出：\n初步診斷: {初步診斷} :\n鑒別診斷：\n1. {鑒別診斷1} ： {所需資訊或檢查1}\n2. {鑒別診斷2} ： {所需資訊或檢查2}\n1. {鑒別診斷3} ： {所需資訊或檢查3}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": summary},
        ],
        temperature=0,
    )
    return response.choices[0].message


def generate_tcm_advice(summary: str) -> str:
    initial_prompt = "你是一個老中醫，請使用你的知識，輔助基層中醫，讓他們提供更全面的診療思路。\n\n請參考病例重點， 提出診斷，鑒別診斷，以及辯證要點\n\n請以以下方式輸出：\n初步診斷: {初步診斷} :\n鑒別診斷：\n1. {鑒別診斷1} ： {所需資訊或檢查1}\n2. {鑒別診斷2} ： {所需資訊或檢查2}\n3. {鑒別診斷3} ： {所需資訊或檢查3}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": summary},
        ],
        temperature=0,
    )
    return response.choices[0].message


async def generate_history_streaming(summary_input: SummaryInput):
    result = generate_clinical_history(summary_input.summary)
    yield {"content": result, "role": "assistant"}


@app.post("/generate_clinical_history")
async def generate_history_endpoint(summary_input: SummaryInput):
    streaming_response = StreamingResponse(generate_history_streaming(summary_input))
    streaming_response.headers["Content-Type"] = "application/json"
    return streaming_response


async def generate_differential_diagnosis_streaming(summary_input: SummaryInput):
    result = generate_differential_diagnosis(summary_input.summary)
    yield {"content": result, "role": "assistant"}


@app.post("/generate_differential_diagnosis")
async def generate_differential_diagnosis_endpoint(summary_input: SummaryInput):
    streaming_response = StreamingResponse(
        generate_differential_diagnosis_streaming(summary_input)
    )
    streaming_response.headers["Content-Type"] = "application/json"
    return streaming_response


async def generate_tcm_advice_streaming(summary_input: SummaryInput):
    result = generate_tcm_advice(summary_input.summary)
    yield {"content": result, "role": "assistant"}


@app.post("/generate_tcm_advice")
async def generate_tcm_advice_endpoint(summary_input: SummaryInput):
    streaming_response = StreamingResponse(generate_tcm_advice_streaming(summary_input))
    streaming_response.headers["Content-Type"] = "application/json"
    return streaming_response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
