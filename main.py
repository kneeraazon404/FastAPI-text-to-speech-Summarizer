from api import app
from database import create_transcriptions_table

if __name__ == "__main__":
    create_transcriptions_table()
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
