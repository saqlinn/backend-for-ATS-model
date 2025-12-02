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
    file_suffix = file.filename.split(".")[-1]
    tmp_name = f"{uuid.uuid4()}.{file_suffix}"
    tmp_path = os.path.join(UPLOAD_DIR, tmp_name)

    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # extract text
    try:
        resume_text = extract_text_from_file(tmp_path)
    except Exception as e:
        os.remove(tmp_path)
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {e}")

    # run analysis
    analysis = analyze_resume_text(resume_text, user_id=user_id, filename=file.filename)

    # save to DB
    db.save_analysis(user_id or "anonymous", file.filename, resume_text, analysis)

    # delete uploaded file to save disk (optional)
    os.remove(tmp_path)

    return analysis

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
