import os,re,json
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from models.api_models import GPT_OSS_20b_GROQ
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_array(contents):
    matches = re.findall(r'\[.*?\]', contents, re.DOTALL)
    
    if not matches:
        return None
    
    longest = max(matches, key=len)
    
    try:
        result = json.loads(longest)
        return result
    except json.JSONDecodeError:
        return None



def questions_from_pdf(contents):
    questions = []
    pdf_text = ""
    doc = fitz.open(stream=contents, filetype="pdf")

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
    
    response = GPT_OSS_20b_GROQ.invoke(f'Extract all questions from this OCR text as a JSON array of strings.  Include any code as part of the question text. Ignore headers, footers, and metadata. OCR Text: {pdf_text} Output only valid JSON array: ["question 1...", "question 2..."]')

    return extract_array(response)