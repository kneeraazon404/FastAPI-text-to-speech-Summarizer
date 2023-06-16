import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI

from database import fetch_transcriptions
from models import SummaryInput
from utils import generate_summary, send_message, transcribe_microphone

from fastapi import APIRouter, FastAPI

router = APIRouter()
app = FastAPI()

# loading environment variables
load_dotenv()

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = ""

# initial prompts for each endpoint
ip_for_clinical_history = os.getenv("INITIAL_PROMPT_FOR_CLINICAL_HISTORY")
ip_for_traumatology_history = os.getenv("INITIAL_PROMPT_FOR_TRAUMATOLOGY_HISTORY")
ip_for_obgyn_history = os.getenv("INITIAL_PROMPT_FOR_OBGYN_HISTORY")
ip_for_differential_diagnosis = os.getenv("INITIAL_PROMPT_FOR_DIFFERENTIAL_DIAGNOSIS")


#  Api endpoints for the frontend to call
@app.get("/transcribe")
def transcribe():
    return {"Transcription": transcribe_microphone()}


@app.get("/summary")
def get_summary():
    language_code = "zh-HK"
    transcriptions = fetch_transcriptions(language_code)

    if not transcriptions:
        return {"Message": "No transcriptions found."}

    summary = generate_summary(transcriptions, language_code)
    return {"Summary": summary}


@app.post("/generate_clinical_history")
async def generate_clinical_history(summary_input: SummaryInput):
    initial_prompt = ip_for_clinical_history
    result = send_message(summary_input.summary, initial_prompt)
    formatted_result = json.dumps(
        {"content": result, "role": "assistant"}, ensure_ascii=False, indent=2
    )
    return formatted_result


@app.post("/generate_differential_diagnosis")
async def generate_differential_diagnosis(summary_input: SummaryInput):
    initial_prompt = ip_for_differential_diagnosis
    result = send_message(summary_input.summary, initial_prompt)
    formatted_result = json.dumps(
        {"content": result, "role": "assistant"}, ensure_ascii=False, indent=2
    )
    return formatted_result


@app.post("/generate_obgyn_history")
async def generate_obgyn_history(summary_input: SummaryInput):
    initial_prompt = ip_for_obgyn_history
    result = send_message(summary_input.summary, initial_prompt)
    formatted_result = json.dumps(
        {"content": result, "role": "assistant"}, ensure_ascii=False, indent=2
    )
    return formatted_result


@app.post("/generate_traumatology_history")
def generate_traumatology_history_endpoint(summary_input: SummaryInput):
    initial_prompt = ip_for_traumatology_history
    result = send_message(summary_input.summary, initial_prompt)
    formatted_result = json.dumps(
        {"content": result, "role": "assistant"}, ensure_ascii=False, indent=2
    )
    return formatted_result
