import os
import azure.cognitiveservices.speech as speechsdk
import openai
from database import save_transcription
from dotenv import load_dotenv

_ = load_dotenv()

subscription_key = os.getenv("SPEECH_KEY")
service_region = os.getenv("SERVICE_REGION")
custom_endpoint = os.getenv("ENDPOINT_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")
gpt_model = os.getenv("GPT_MODEL")
language_code = os.getenv("LANGUAGE_CODE")


def generate_summary(transcriptions, language_code):
    # Join all transcriptions into a single string
    transcription_text = " ".join(transcriptions)

    # Generate summary using OpenAI GPT-3.5 model
    prompt = f"[{language_code}] Please summarize the following transcriptions:\n{transcription_text}\nSummary:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    summarized_text = response.choices[0].text.strip()
    return summarized_text


def transcribe_microphone():
    language_code = "zh-HK"
    speech_config = speechsdk.SpeechConfig(
        subscription=subscription_key, region=service_region
    )
    speech_config.endpoint_id = custom_endpoint
    speech_config.speech_recognition_language = language_code
    audio_config = speechsdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )

    done = False
    transcription = ""

    def stop_cb(evt):
        nonlocal done
        done = True

    def speech_recognized(evt):
        nonlocal transcription
        result = evt.result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            transcription += result.text

    speech_recognizer.recognized.connect(speech_recognized)
    speech_recognizer.session_stopped.connect(stop_cb)

    speech_recognizer.start_continuous_recognition()

    # Keep transcribing until manually stopped
    while not done:
        pass

    speech_recognizer.stop_continuous_recognition()

    # Save transcription to SQLite database
    save_transcription(transcription, language_code)

    return transcription


def send_message(summary: str, initial_prompt) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": summary},
        ],
        temperature=0,
    )
    return response.choices[0].message
