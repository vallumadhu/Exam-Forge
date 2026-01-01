import requests
import json
from groq import Groq
from config import GROQ_API_KEY

class ChatModel:
    def __init__(self, model_name: str = "openai/gpt-oss-20b", api_key: str = GROQ_API_KEY):
        self.model_name = model_name
        self.client = Groq(api_key=api_key)

    def invoke(self, prompt: str = "", messages: list = None, k_chunks: list = None):
        messages = messages or []
        messages.append({"role": "user", "content": prompt})

        if k_chunks:
            context = "\n\n".join(
                f"chunk index:{c['metadata']['chunk_index']}\nchunk data:\n{c['metadata']['text']}" 
                for c in k_chunks
            )
            messages.insert(0, {"role": "system", "content": f"Use the following context to answer the user's question:\n\n{context}"})

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=1,
            max_completion_tokens=8192,
            top_p=1,
            reasoning_effort="medium",
            stream=False,
            stop=None
        )


        return completion.choices[0].message.content

    def info(self):
        return {"model_name": self.model_name, "accessed_using": "Groq API"}

GPT_OSS_20b_GROQ = ChatModel()