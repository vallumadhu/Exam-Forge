import os,re,json,sys
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from models.api_models import GPT_OSS_20b_GROQ

def get_tesseract_path():

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    tesseract_exe = os.path.join(base_path, 'tesseract', 'tesseract.exe')

    if not os.path.exists(tesseract_exe):
        raise FileNotFoundError(f"Tesseract not found at: {tesseract_exe}")
    
    return tesseract_exe

pytesseract.pytesseract.tesseract_cmd = get_tesseract_path()

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