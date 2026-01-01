import os,sys
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from services.textformat import clean_text


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

def extract_text_from_pdf(contents):
    pdf_text = ""
    doc = fitz.open(stream=contents, filetype="pdf")

    for page in doc:
        text = page.get_text()

        pdf_text+=clean_text(text)
        pdf_text+="\n"

        for img in page.get_images(full=True):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            if pix.n > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            img_pil = Image.frombytes("RGB",(pix.width, pix.height),pix.samples)

            ocr_text = pytesseract.image_to_string(img_pil)

            pdf_text+=clean_text(ocr_text)
            pdf_text+="\n"

            pix = None

    return pdf_text