# main.py
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, uuid
from pipeline import analyze_resume_text
import db

app = FastAPI(title="ATS Resume Analyzer API")

# allow frontend on lovables host or local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "ATS Resume Analyzer API is live!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
db.init_db()

# helper to extract text
def extract_text_from_file(path: str):
    ext = path.split(".")[-1].lower()
    if ext == "pdf":
        import fitz
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif ext in ("docx", "doc"):
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        # fallback to read as text
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

@app.post("/v1/analyzeResume")
async def analyze_resume(user_id: str = Form(None), file: UploadFile = File(...)):
    # save uploaded file
    original_filename = file.filename or "resume"
    file_suffix = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "bin"
    tmp_name = f"{uuid.uuid4()}.{file_suffix}"
    tmp_path = os.path.join(UPLOAD_DIR, tmp_name)

    try:
        with open(tmp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            resume_text = extract_text_from_file(tmp_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract text: {e}") from e

        analysis = analyze_resume_text(resume_text, user_id=user_id, filename=original_filename)
        db.save_analysis(user_id or "anonymous", original_filename, resume_text, analysis)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return analysis

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
