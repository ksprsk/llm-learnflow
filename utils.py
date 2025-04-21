import re
import time
import json
import tiktoken
from pathlib import Path
import hooks
# Token counting function
def count_tokens(text, model="gpt-3.5-turbo"):
    """Count the number of tokens in a text string."""
    try:
        encoder = tiktoken.encoding_for_model(model)
        return len(encoder.encode(text))
    except:
        # Fallback approximation: ~4 characters per token
        return len(text) // 4

def load_prompt(prompt_name):
    """Load a prompt template from the prompts directory."""
    prompt_path = Path("prompts") / f"{prompt_name}.txt"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Prompt template '{prompt_name}' not found")

def process_text(text, api_adapter):
    """
    Process the input text to generate summary, chunks, and concept map.
    
    Args:
        text (str): The input text to process
        api_adapter: The API adapter to use for LLM requests
    
    Returns:
        tuple: (summary, chunks, concept_map)
    """
    # Apply hooks before processing
    text = hooks.on_text_process(text)
    
    # Generate summary
    summary_prompt = load_prompt("summary")
    summary_prompt = summary_prompt.replace("{{TEXT}}", text)
    summary = api_adapter.generate_completion(summary_prompt)
    
    # Apply hooks after summary generation
    summary = hooks.on_summary_generate(summary)
    
    # Generate chunks
    chunking_prompt = load_prompt("chunking")
    chunking_prompt = chunking_prompt.replace("{{TEXT}}", text)
    chunks_json = api_adapter.generate_completion(chunking_prompt)
    
    try:
        # Parse the JSON response
        chunks_data = json.loads(chunks_json)
        chunks = chunks_data.get("chunks", [])
        
        # Add estimated reading time for each chunk (rough estimation)
        for chunk in chunks:
            word_count = len(chunk["content"].split())
            # Assuming average reading speed of 200 words per minute
            chunk["estimated_time"] = max(1, round(word_count / 200))
    except json.JSONDecodeError:
        # If JSON parsing fails, create a single chunk
        chunks = [{
            "title": "Full Text",
            "content": text,
            "estimated_time": max(1, round(len(text.split()) / 200))
        }]
    
    # Apply hooks after chunk generation
    chunks = hooks.on_chunk_generate(chunks)
    
    # Generate concept map
    concept_map_prompt = load_prompt("concept_map")
    concept_map_prompt = concept_map_prompt.replace("{{TEXT}}", text)
    concept_map_json = api_adapter.generate_completion(concept_map_prompt)
    
    try:
        concept_map = json.loads(concept_map_json)
    except json.JSONDecodeError:
        concept_map = {"error": "Failed to generate concept map", "nodes": [], "edges": []}
    
    # Apply hooks after concept map generation
    concept_map = hooks.on_concept_map_generate(concept_map)
    
    return summary, chunks, concept_map

def highlight_text(text, phrases_to_highlight):
    """
    Add HTML highlighting to specific phrases in text.
    
    Args:
        text (str): The text to highlight
        phrases_to_highlight (list): List of phrases to highlight
    
    Returns:
        str: HTML-formatted text with highlights
    """
    highlighted_text = text
    for phrase in phrases_to_highlight:
        if not phrase or len(phrase) < 3:
            continue  # Skip very short phrases
            
        # Escape special regex characters
        escaped_phrase = re.escape(phrase)
        # Add highlight span tags
        highlighted_text = re.sub(
            f"({escaped_phrase})",
            r'<span class="highlight">\1</span>',
            highlighted_text,
            flags=re.IGNORECASE
        )
    return highlighted_text

def create_concept_map(concept_data):
    """
    Create a concept map visualization from the concept data.
    In a real implementation, this would use a visualization library.
    
    Args:
        concept_data (dict): The concept map data
    
    Returns:
        dict: The formatted concept map for visualization
    """
    # This is a placeholder. In a real implementation, this would
    # create a proper visualization using a library like Graphviz or d3.js
    return concept_data

def convert_to_flashcards(text, api_adapter):
    """
    Convert text to flashcards using the API.
    
    Args:
        text (str): The text to convert to flashcards
        api_adapter: The API adapter to use for LLM requests
    
    Returns:
        list: List of flashcard dictionaries with 'question' and 'answer' keys
    """
    flashcard_prompt = load_prompt("flashcard")
    flashcard_prompt = flashcard_prompt.replace("{{TEXT}}", text)
    flashcard_json = api_adapter.generate_completion(flashcard_prompt)
    
    try:
        # Parse the JSON response
        flashcards_data = json.loads(flashcard_json)
        flashcards = flashcards_data.get("flashcards", [])
    except json.JSONDecodeError:
        # If JSON parsing fails, return empty list
        flashcards = []
    
    # Apply hooks after flashcard creation
    flashcards = hooks.on_flashcard_create(flashcards)
    
    return flashcards

def generate_chunks(text, min_chunk_size=500, max_chunk_size=1500):
    """
    Simple rule-based chunking algorithm that respects paragraph and section boundaries.
    For more sophisticated chunking, use the API-based approach in process_text().
    
    Args:
        text (str): Text to chunk
        min_chunk_size (int): Minimum chunk size in characters
        max_chunk_size (int): Maximum chunk size in characters
    
    Returns:
        list: List of chunk dictionaries
    """
    # Split by double newlines (paragraphs)
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    current_title = "Introduction"
    
    for para in paragraphs:
        para_size = len(para)
        
        # Check if this is a heading
        heading_match = re.match(r'^#{1,6}\s+(.+)$', para) or re.match(r'^(.+)\n[=\-]{3,}$', para)
        
        if heading_match:
            # If we have content and either this is a major heading or the chunk is big enough
            if current_chunk and (para.startswith('# ') or current_size >= min_chunk_size):
                # Save the current chunk
                chunk_content = '\n\n'.join(current_chunk)
                chunks.append({
                    "title": current_title,
                    "content": chunk_content,
                    "estimated_time": max(1, round(len(chunk_content.split()) / 200))
                })
                
                # Start a new chunk with the heading
                current_title = heading_match.group(1)
                current_chunk = [para]
                current_size = para_size
            else:
                # Add heading to current chunk
                current_chunk.append(para)
                current_size += para_size
                # Update title if this is the first content or a major heading
                if not current_chunk or para.startswith('# '):
                    current_title = heading_match.group(1)
        else:
            # If adding this paragraph would exceed max_chunk_size, start a new chunk
            if current_size + para_size > max_chunk_size and current_size >= min_chunk_size:
                chunk_content = '\n\n'.join(current_chunk)
                chunks.append({
                    "title": current_title,
                    "content": chunk_content,
                    "estimated_time": max(1, round(len(chunk_content.split()) / 200))
                })
                
                # Start new chunk with this paragraph
                # Use the first sentence as title if not a heading
                first_sentence = re.match(r'^([^.!?]+[.!?])', para)
                current_title = (first_sentence.group(1) if first_sentence else "Continued") + "..."
                current_chunk = [para]
                current_size = para_size
            else:
                # Add to current chunk
                current_chunk.append(para)
                current_size += para_size
    
    # Add the last chunk if there's anything left
    if current_chunk:
        chunk_content = '\n\n'.join(current_chunk)
        chunks.append({
            "title": current_title,
            "content": chunk_content,
            "estimated_time": max(1, round(len(chunk_content.split()) / 200))
        })
    
    return chunks
