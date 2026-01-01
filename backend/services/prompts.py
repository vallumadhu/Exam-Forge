from models.api_models import GPT_OSS_20b_GROQ
from services.textformat import extract_array
import json

def notes_from_text(pdf_text):
    prompt = f"""
        The following text is OCR output from a notes PDF and may contain noise, missing words, and junk text.

        Clean and correct the content, remove irrelevant text, and reconstruct words where possible.
        Present the final clean notes clearly.
                                      
        Output ONLY the notes between:--starts here --ends here . Text{pdf_text}"""
    
    results = GPT_OSS_20b_GROQ.invoke(prompt)
    
    return results

   

def questions_from_text(pdf_text):
    prompt = f"""
        Extract all questions from the following text.

        Rules:
        - Return ONLY a valid JSON array of strings
        - Include code blocks as part of the question
        - Ignore headers, footers, and metadata

        Output format:
        ["Question 1", "Question 2"] . Text{pdf_text}"""
    
    response = GPT_OSS_20b_GROQ.invoke(prompt)
    
    return extract_array(response)

def generate_topics(text):
    prompt = f"""
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
    topics = GPT_OSS_20b_GROQ.invoke(prompt)

    return json.loads(topics)

def results_dict_to_text(results_by_topic): 
    texts = []

    for topic in results_by_topic:
        topic_block = f"Topic: {topic[0]} "
        topic_block += f"Related content: {topic[1:]}"

        texts.append(topic_block.strip())

    return texts

def topic_to_notes(text_to_model):
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