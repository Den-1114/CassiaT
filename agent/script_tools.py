import pymupdf
import json
import docx

def extract_info_from_file(file_path):
    """
    Extract text from a file (PDF, TXT, DOCX) and return it.
    """
    text = ""

    # Get file extension
    if '.' in file_path:
        file_ext = file_path.split('.')[-1].lower()
    else:
        raise ValueError("File has no extension")

    # Handle different file types
    if file_ext == 'pdf':
        doc = pymupdf.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    elif file_ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif file_ext == 'docx':
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + '\n'
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

    return text


def extract_hotel_info(agent_executor, text):
    """
    Extract building and facility information from the provided text using the agent.
    """
    response = agent_executor.invoke({"text": text})
    return response["output"]

def clean_hotel_info(hotel_info):
    cleaned = hotel_info.removeprefix("```json").removesuffix("```").strip()
    data = json.loads(cleaned)
    return data