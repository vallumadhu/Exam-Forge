import os,re,json,sys
import fitz  # PyMuPDF
import pytesseract
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PIL import Image
from pinecone import Pinecone , ServerlessSpec 
import uuid
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

api_key = os.getenv("GROQ_API_KEY")


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
    
def clean_text(text: str) -> str:
    text = re.sub(r'\f|\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

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

def notes_from_pdf(contents):
    pdf_text = extract_text_from_pdf(contents)
    results = GPT_OSS_20b_GROQ.invoke(f"""
        The following text is OCR output from a notes PDF and may contain noise, missing words, and junk text.

        Clean and correct the content, remove irrelevant text, and reconstruct words where possible.
        Present the final clean notes clearly.
                                      
        Output ONLY the notes between:--starts here (clean notes) --ends here . Text{pdf_text}""")
    
    return extract_array(results)

   

def questions_from_pdf(contents):
    pdf_text = extract_text_from_pdf(contents)
    
    response = GPT_OSS_20b_GROQ.invoke( f"""
        Extract all questions from the following text.

        Rules:
        - Return ONLY a valid JSON array of strings
        - Include code blocks as part of the question
        - Ignore headers, footers, and metadata

        Output format:
        ["Question 1", "Question 2"] . Text{pdf_text}""")
    
    return extract_array(response)

def chunks(contents):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 20
    )

    chunks = text_splitter.split_text(contents)
    return chunks

def embeddings(chunks):

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings_vectors = model.encode(chunks)
    return embeddings_vectors

def vector_database(chunks, embeddings_vectors, index_name="python3"):
    
    pc = Pinecone(api_key=api_key)
    
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=384,  
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    index = pc.Index(index_name)

    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_vectors)):
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embedding.tolist(),
            "metadata": {
                "text": chunk,
                "chunk_id": i
            }
        })

    
    index.upsert(vectors=vectors)

    return {
        "status": "success",
        "vectors_uploaded": len(vectors),
        "index_name": index_name
    }

def generate_topics(text):
    topics = GPT_OSS_20b_GROQ.invoke(
    f"""
    The following text contains cleaned study notes.

    Task:
    - Identify the main topic titles present in the text.
    - For each topic, include a few relevant keywords to help identify it.
    - Ignore examples, subpoints, and detailed explanations.
    - Avoid duplicates and keep topic names concise.

    Output Rules:
    - Return ONLY a valid JSON array.
    - Each item must be an array where:
      - First element is the topic title (string)
      - Remaining elements are keywords (strings)
    - Do NOT include any explanation or extra text.

    Output format example:
    [
      ["Topic 1", "keyword1", "keyword2"],
      ["Topic 2", "keyword1", "keyword2"]
    ]

    Text:
    {text}
    """
)

    return topics

#sending the queries  to the questions database to get the similar 5 questions
def query_pinecone(topics , index_name = "python4" , top_k = 5):
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    query_embeddings = embeddings(topics)
    results_by_topic = {}

    for topic, query_vector in zip(topics, query_embeddings):
        response = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )

        results_by_topic[topic] = [ #storing the values in the dictionary
            {
                "score": match["score"],
                "text": match["metadata"]["text"]
            }
            for match in response["matches"]
        ]

        return results_by_topic


    
#making the dictionary into the text so that it would be again converted into an embeddings
def results_dict_to_text(results_by_topic): 
    #frst pass the dict from the topics function and then pass t
    #dict from the notes function
    texts = []

    for topic, matches in results_by_topic.items():
        topic_block = f"Topic: {topic}\n"
        topic_block += "Related content:\n"

        for m in matches:
            topic_block += f"- {m['text']}\n"

        texts.append(topic_block.strip())

    return texts


# notes = query_pinecone(texts , index_name="python3" , top_k=5)
#text_to_model = results_dict_to_text(notes)


#create a function to , make the model to give the concise answers  and the same type of questions

def output(text_to_model):
    results = {}
    for topic , text in text_to_model.items():
        response = GPT_OSS_20b_GROQ.invoke(f""" 
            The following text is study material related to the topic "{topic}".

            Tasks:
            1. Generate concise and easy-to-understand notes for this topic.
            2. Do NOT elaborate excessively.
            3. Generate exactly 10 practice questions based on the topic.

            Output format (STRICT):
            Topic: {topic}

            Concise Notes:
            - point 1
            - point 2
            - point 3

            Practice Questions:
            1. Question one
            2. Question two
            ...
            10. Question ten

            Text:
            {text}
                """)
        results[topic] = response
    return results




