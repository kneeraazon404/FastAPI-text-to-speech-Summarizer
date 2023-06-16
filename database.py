import sqlite3
from models import Transcription


def create_transcriptions_table():
    conn = sqlite3.connect("sqlite3.db")
    cursor = conn.cursor()
    cursor.execute(
        f"""CREATE TABLE IF NOT EXISTS {Transcription.table} (
        {Transcription.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        {Transcription.transcription} TEXT,
        {Transcription.language_code} TEXT
        )"""
    )
    conn.commit()
    conn.close()


def save_transcription(transcription, language_code):
    conn = sqlite3.connect("sqlite3.db")
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO {Transcription.table} ({Transcription.transcription}, {Transcription.language_code}) VALUES (?, ?)",
        (transcription, language_code),
    )
    conn.commit()
    conn.close()


def fetch_transcriptions(language_code):
    conn = sqlite3.connect("sqlite3.db")
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT {Transcription.transcription} FROM {Transcription.table} WHERE {Transcription.language_code}=?",
        (language_code,),
    )
    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]
