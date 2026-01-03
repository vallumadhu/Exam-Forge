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

def generate_keywords(question_list:list,already_generated:list):
    prompt = f"""
            You are generating keywords for semantic retrieval from a vector database.

            Input questions:
            {question_list}

            Already generated keywords (avoid repeating these unless essential):
            {already_generated}

            Task:
            Generate at most **4 concise, high-signal keywords** that best capture the **core concepts** of the questions and are likely to appear in study notes or textbooks.

            Rules:
            - Return the output as a **single plain string**, comma-separated:
            "keyword1, keyword2, keyword3, keyword4"
            - Do NOT use code blocks, lists, quotes, or explanations.
            - Prefer conceptual and canonical terms over surface wording.
            - Expand abbreviations and infer equivalent or underlying concepts.
            - Avoid redundancy with already generated keywords unless unavoidable.

            Examples:
            - "second law of thermodynamics" → entropy
            - "TIR" → total internal reflection
            - "rate of reaction" → reaction kinetics, rate law
            - "acid strength" → pKa, Ka
            - "hashing" → hash function, hash table
            - "recursion" → call stack, base case

            Output only the keyword string. Nothing else."""

    response = GPT_OSS_20b_GROQ.invoke(prompt)
    return response

def generate_notes(chunks,questions,keywords):
    prompt = f"""
    You are an expert academic content writer.
    
    Input Text Chunks:
    {"\n".join(chunks)}
    
    Questions to Guide Notes:
    {questions}
    
    Keywords to Focus On:
    {keywords}
    
    Task:
    - Generate **comprehensive study notes** covering all important points in the text.
    - Notes must be **directly relevant** to the input questions and keywords.
    - Consider other possible questions related to the content to ensure completeness, 
      but do NOT include those additional questions in the notes.
    - Notes should be structured, clear, and self-contained. Include definitions, examples,
      and explanations as needed to fully understand the concepts.
    - Do not include any unrelated content.
    - Do not format as Q&A. Notes only.
    
    Output:
    Return the notes as a single plain text block. Do not include markdown, code blocks,
    or any extra formatting.
    """

    response = GPT_OSS_20b_GROQ.invoke(prompt)
    
    return response

def generate_questions(note,questions,keywords):

    prompt = f"""
    You are an expert educator preparing exam questions.

    Input Study Notes:
    {note}

    Original Questions:
    {questions}

    Keywords:
    {keywords}

    Task:
    - Generate **2-6 new plausible exam questions** based on the notes.
    - Questions must be conceptually aligned with the original questions, study notes and keywords.
    - Questions should be similar in style to previous exam questions (pyq style).
    - Do not repeat the original questions verbatim.
    - Return as a plain Python list of strings.

    Example Output:
    ["Question 1?", "Question 2.", "Question 3?", ...]
    """
    response = GPT_OSS_20b_GROQ.invoke(prompt)


    return extract_array(response)
