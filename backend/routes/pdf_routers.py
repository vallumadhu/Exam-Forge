from fastapi import APIRouter,UploadFile, File
from services.pdf2text import questions_from_pdf


router = APIRouter()

@router.post("/pdf2questions")
async def pdf2questions(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        return {"error": "Unsupported file type, please upload a pdf."}
    
    contents = await file.read()
    questions = questions_from_pdf(contents)

    return {"questions":questions}
