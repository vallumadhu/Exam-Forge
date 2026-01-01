from fastapi import APIRouter,UploadFile, File
from services.pdf2text import extract_text_from_pdf
from services.prompts import questions_from_text,notes_from_text
from services.textformat import extract_notes_response


router = APIRouter()

@router.post("/pdf2questions")
async def pdf2questions(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        return {"error": "Unsupported file type, please upload a pdf."}
    
    contents = await file.read()
    pdf_text = extract_text_from_pdf(contents)
    questions = questions_from_text(pdf_text)

    return {"questions":questions}

@router.post("/pdf2notes")
async def pdf2notes(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        return {"error": "Unsupported file type, please upload a pdf."}
    
    contents = await file.read()
    pdf_text = extract_text_from_pdf(contents)
    notes = notes_from_text(pdf_text)
    notes = extract_notes_response(notes)

    return {"notes":notes}