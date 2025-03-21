from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from parser import extract_tasks_from_pdf
import os
import shutil

app = FastAPI(
    title="PDF Task Extraction API",
    description="Upload a PDF to extract maintenance tasks and get a JSON response.",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to the PDF Task Extraction API!"}

@app.post("/extract-tasks/")
async def extract_tasks(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"

    # Save uploaded file temporarily
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file. Error: {str(e)}")

    try:
        tasks_json = extract_tasks_from_pdf(temp_file_path)

        return JSONResponse(content={
            "raw_tasks": tasks_json
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
