from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")



def chunks(contents,chunk_size=500,chunk_overlap = 20):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
    )

    chunks = text_splitter.split_text(contents)
    return chunks

def embeddings(chunks,model=embedding_model):
    embeddings_vectors = model.encode(chunks)
    return embeddings_vectors