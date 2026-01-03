from pinecone import Pinecone,ServerlessSpec
from uuid import uuid4
from config import Pinecone_API_KEY
from models.embedding_model import embeddings

pc = Pinecone(api_key=Pinecone_API_KEY)

class PineconeDB:
    def __init__(self,index_name):
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
        self.index = pc.Index(index_name)
        self.index_name = index_name
    
    def push(self,chunks, embeddings_vectors):
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_vectors)):
            vectors.append({
                "id": str(uuid4()),
                "values": embedding.tolist(),
                "metadata": {
                    "text": chunk,
                    "chunk_id": i
                }
            })

        self.index.upsert(vectors=vectors)

        return {
            "status": "success",
            "vectors_uploaded": len(vectors),
            "index_name": self.index_name
        }
    
    def query(self,query,top_k = 5):
        embedded_query = embeddings(query)
        response = self.index.query(
            vector=embedded_query.tolist(),
            top_k=top_k,
            include_metadata=True
        )

        return [match['metadata'] for match in response['matches']]


    
    def DELETEDB(self):
        pc.delete_index(self.index_name)



def retriveQuestionFromDB(topics , PineconeDB , top_k = 5):
    query_embeddings = embeddings(topics)
    results_by_topic = {}

    for topic, query_vector in zip(topics, query_embeddings):
        response = PineconeDB.query(query_vector,top_k=top_k)

        results_by_topic[topic] = [ #storing the values in the dictionary
            {
                "score": match["score"],
                "text": match["metadata"]["text"]
            }
            for match in response["matches"]
        ]

        return results_by_topic