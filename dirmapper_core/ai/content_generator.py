# dirmapper_core/ai/content_generator.py
from logging import config
import os
from typing import List
from openai import OpenAI, AuthenticationError

from dirmapper_core.models.directory_item import DirectoryItem

def generate_file_content(path: str, items: List['DirectoryItem'], root_dir: str) -> str:
    # Build prompt
    prompt = build_prompt(path, items, root_dir)
    
    if not os.environ['OPENAI_API_KEY']:
        raise ValueError("API token is not set. Please set the API token in the preferences.")
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that generates file content."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )

    generated_content = response['choices'][0]['message']['content'].strip()
    return generated_content

def build_prompt(path: str, items: List[DirectoryItem], root_dir: str) -> str:
    project_summary = "This project is about..."
    directory_context = "The project has the following structure:\n"
    # Create a hierarchical view of items
    for item in items:
        indent = '    ' * item.level
        directory_context += f"{indent}{item.name}\n"

    prompt = (
        f"{project_summary}\n\n"
        f"{directory_context}\n\n"
        f"Generate content for the file at '{path}'."
    )
    return prompt
