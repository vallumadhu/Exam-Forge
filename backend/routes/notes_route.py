from fastapi import APIRouter,Query
from db.pinecone import PineconeDB
from pydantic import BaseModel
from models.embedding_model import embedding_model,embeddings,chunks
from services.prompts import generate_topics,results_dict_to_text,topic_to_notes

class Data(BaseModel):
    note:str
    questions:list

router = APIRouter()


@router.post("/generatenotes")
async def pushnotes(body: Data, index_name:str= Query(...)):
    note = body.note
    questions = body.questions
    generated_notes = []
    topics = generate_topics(note)
    topics = results_dict_to_text(topics)

    # for topic in topics:
    #     gen_note = topic_to_notes(topic)
    #     generated_notes.append(gen_note)


    return {"output":generated_notes}