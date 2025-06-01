from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
import subprocess
from datetime import datetime

app = FastAPI()

LOG_FILE = "scripts/logs.txt"

@app.post("/upload-script/")
async def upload_script(file: UploadFile = File(...)):
    script_path = os.path.join("scripts", file.filename)
    with open(script_path, "wb") as f:
        f.write(await file.read())
    return {"message": f"Script '{file.filename}' subido correctamente."}

@app.post("/run-script/")
def run_script(filename: str):
    script_path = os.path.join("scripts", filename)
    if not os.path.exists(script_path):
        return JSONResponse(status_code=404, content={"error": "Script no encontrado"})

    try:
        result = subprocess.run(["python", script_path], capture_output=True, text=True, timeout=30)
        log_entry = f"[{datetime.now()}] {filename} -> {result.stdout}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as logf:
            logf.write(log_entry)
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

@app.get("/logs/")
def get_logs():
    if not os.path.exists(LOG_FILE):
        return {"logs": []}
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return {"logs": f.read().splitlines()}
