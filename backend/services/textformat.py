import re,json

def clean_text(text: str) -> str:
    text = re.sub(r'\f|\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

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


def extract_notes_response(contents):

    matches = re.findall(r'--starts here(.*?)--ends here',contents,re.DOTALL)
    if not matches:
        return None
    
    return max(matches, key=len)