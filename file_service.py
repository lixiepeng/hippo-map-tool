# pip install fastapi uvicorn aiofiles
# uvicorn file_service:app --host 0.0.0.0 --port 8095 --reload
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/download/{file_name}")
async def download(file_name: str):
    return FileResponse(f"./download/{file_name}")