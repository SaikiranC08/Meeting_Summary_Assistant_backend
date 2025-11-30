# main.py
from fastapi import FastAPI, Body, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

from extract.summarizer import MeetingSummarizer
from extract.pdf_reader import extract_text_from_pdf
from llm.gemini_client import GeminiClient

app = FastAPI(title="Meeting Summarizer (MVP - Summary Only)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM Client
llm  = GeminiClient(model="models/gemini-2.5-flash-preview-09-2025")
summarizer = MeetingSummarizer(llm_client=llm)


class SummarizeRequest(BaseModel):
    text: str


@app.get("/")
def root():
    return {"status": "backend is running"}


@app.post("/api/summarize-meeting")
async def api_summarize_meeting(payload: SummarizeRequest = Body(...)):
    """Summaries only - Phase B."""
    try:
        if not payload.text.strip():
            raise HTTPException(400, "Text cannot be empty.")

        response = summarizer.generate_summary(payload.text)
        return response

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@app.post("/api/upload-pdf")
async def api_upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF, extract text, run summarizer, return JSON result."""
    try:
        # FIXED: endswith()
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        contents = await file.read()
        text = extract_text_from_pdf(contents)

        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF text extraction returned empty content.")

        response = summarizer.generate_summary(text)
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
