from fastapi import APIRouter,Body,Query
from db.pinecone import PineconeDB
from pydantic import BaseModel
from models.embedding_model import embedding_model,embeddings,chunks

class Note(BaseModel):
    note:str

class Questions(BaseModel):
    questions:list

router = APIRouter()


@router.post("/pushnotes")
async def pushnotes(body: Note, index_name:str= Query(...)):
    note = body.note

    db = PineconeDB(index_name)

    note_chunks = chunks(note)
    note_embeddings = embeddings(note_chunks)
    db.push(note_chunks,note_embeddings)

    return {"message":"pushed successfully"}

@router.post("/pushquestions")
async def pushquestions(body: Questions, index_name:str= Query(...)):
    questions = body.questions
    db = PineconeDB(index_name)

    question_embeddings = embeddings(questions)
    db.push(questions,question_embeddings)

    return {"message":"pushed successfully"}