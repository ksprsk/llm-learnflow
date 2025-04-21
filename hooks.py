"""
Hook system for the AI Learning Framework.
This allows extending the application at specific points without modifying the core code.
"""

def on_app_load():
    """Hook called when the application is loaded."""
    # This function can be modified by users to add custom logic
    pass

def on_app_close():
    """Hook called when the application is closed."""
    # This function can be modified by users to add custom logic
    pass

def on_text_process(text):
    """
    Hook called before processing text.
    
    Args:
        text (str): The text to be processed
    
    Returns:
        str: The text after any modifications
    """
    # This function can be modified by users to add custom logic
    return text

def on_summary_generate(summary):
    """
    Hook called after generating a summary.
    
    Args:
        summary (str): The generated summary
    
    Returns:
        str: The summary after any modifications
    """
    # This function can be modified by users to add custom logic
    return summary

def on_chunk_generate(chunks):
    """
    Hook called after generating chunks.
    
    Args:
        chunks (list): The generated chunks
    
    Returns:
        list: The chunks after any modifications
    """
    # This function can be modified by users to add custom logic
    return chunks

def on_concept_map_generate(concept_map):
    """
    Hook called after generating a concept map.
    
    Args:
        concept_map (dict): The generated concept map
    
    Returns:
        dict: The concept map after any modifications
    """
    # This function can be modified by users to add custom logic
    return concept_map

def on_flashcard_create(flashcards):
    """
    Hook called after creating flashcards.
    
    Args:
        flashcards (list): The created flashcards
    
    Returns:
        list: The flashcards after any modifications
    """
    # This function can be modified by users to add custom logic
    return flashcards

def on_qa_generate(question, answer):
    """
    Hook called after generating a Q&amp;A pair.
    
    Args:
        question (str): The question
        answer (str): The generated answer
    
    Returns:
        tuple: The (question, answer) pair after any modifications
    """
    # This function can be modified by users to add custom logic
    return question, answer

def on_error(error, context=None):
    """
    Hook called when an error occurs.
    
    Args:
        error (Exception): The error that occurred
        context (dict, optional): Additional context about the error
    
    Returns:
        None
    """
    # This function can be modified by users to add custom error handling
    pass

def on_flashcard_export(flashcards, format_type):
    """
    Hook called before exporting flashcards.
    
    Args:
        flashcards (list): List of flashcards to export
        format_type (str): Export format (e.g., 'anki', 'csv')
    
    Returns:
        list: The flashcards after any modifications
    """
    # This function can be modified by users to add custom export logic
    return flashcards
