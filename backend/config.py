from dotenv import load_dotenv
import os
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
Pinecone_API_KEY = os.getenv("Pinecone_API_KEY")