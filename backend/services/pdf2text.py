import os,re
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from models.small_models import model
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

base = os.path.abspath("./temp_data")


def questions_from_pdf(pdf_path):
    questions = []
    pdf_text = ""
    doc = fitz.open(pdf_path)

    for page in doc:
        text = page.get_text()

        clean_text = re.sub(r'\f|\n+', '\n', text)
        clean_text = re.sub(r' +', ' ', clean_text)

        pdf_text+=text
        pdf_text+="\n"


        for img in page.get_images(full=True):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            if pix.n > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            img_pil = Image.frombytes("RGB",(pix.width, pix.height),pix.samples)

            text = pytesseract.image_to_string(img_pil)

            clean_text = re.sub(r'\f|\n+', '\n', text)
            clean_text = re.sub(r' +', ' ', clean_text)

            pdf_text+=text
            pdf_text+="\n"

            pix = None
    
    response = model.invoke(f'Extract all questions from this OCR text as a JSON array of strings.  Include any code as part of the question text. Ignore headers, footers, and metadata. OCR Text: {pdf_text} Output only valid JSON array: ["question 1...", "question 2..."]')
    print(response)


pdf_path = os.path.join(base, "sample.pdf")
questions_from_pdf(pdf_path)