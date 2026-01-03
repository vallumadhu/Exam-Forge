from fastapi import APIRouter,Query
from db.pinecone import PineconeDB
from pydantic import BaseModel
from models.embedding_model import embedding_model,embeddings,chunks
from services.prompts import generate_topics,results_dict_to_text,topic_to_notes,generate_keywords,generate_notes,generate_questions
from models.k_means import K_means

class Data(BaseModel):
    questions:list

router = APIRouter()


@router.post("/generatenotes")
async def pushnotes(body: Data, index_name:str= Query(...)):
    pinecone_db = PineconeDB(index_name)
    questions = body.questions
    
    k_means = K_means(questions)
    question_clustors = k_means.get_clustors()

    data_blocks = []

    for question_list in question_clustors:
        keywords = generate_keywords(question_list,data_blocks)

        block = {
            "question_list":question_list,
            "keywords":keywords
        }

        data_blocks.append(block)
    

    queries = [f"Questions: {" ".join(block['question_list'])} Keywords: {block['keywords']}" for block in data_blocks]

    chunk_ids = []

    for i in range(len(queries)):
        chunks = pinecone_db.query(queries[i])
        chunks.sort(key= lambda x:x["chunk_id"])

        unique_chunks = []
        current_chunk_ids = []

        for chunk in chunks:
            if chunk["chunk_id"] not in chunk_ids:
                current_chunk_ids.append(chunk["chunk_id"])
                unique_chunks.append(chunk["text"])
        
        chunk_ids.extend(current_chunk_ids)
            
        data_blocks[i]["chunks"]=unique_chunks
    
    for i in range(len(data_blocks)):
        data = data_blocks[i]
        
        notes = generate_notes(data['chunks'], data['question_list'], data['keywords'])
        data['notes'] = notes

        questions = generate_questions(notes, data['question_list'], data['keywords'])

        data["more_questions"] = []

        if questions:
            data["more_questions"].append(questions)


    return {"output":data_blocks}