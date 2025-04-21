"""
Custom widgets for the AI Learning Framework.
These widgets extend the base Streamlit functionality.
"""

import streamlit as st
import pandas as pd
import uuid

def flashcard_viewer(flashcards, key_prefix="fc"):
    """
    Display flashcards in a Streamlit UI.
    
    Args:
        flashcards (list): List of flashcard dictionaries with 'question' and 'answer' keys
        key_prefix (str, optional): Prefix for widget keys. Defaults to "fc".
    
    Returns:
        None
    """
    if not flashcards:
        st.info("No flashcards available.")
        return
    
    # Create tabs for different view modes
    tab1, tab2 = st.tabs(["Study Mode", "List View"])
    
    with tab1:
        # Study mode with flip cards
        st.write("### Flashcard Study")
        
        # Initialize state for current card if not exists
        if f"{key_prefix}_current_card" not in st.session_state:
            st.session_state[f"{key_prefix}_current_card"] = 0
        
        # Get current card index
        current_idx = st.session_state[f"{key_prefix}_current_card"]
        
        # Display card navigation
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if current_idx > 0:
                if st.button("← Previous", key=f"{key_prefix}_prev"):
                    st.session_state[f"{key_prefix}_current_card"] -= 1
                    st.rerun()
        
        with col2:
            st.write(f"Card {current_idx + 1} of {len(flashcards)}")
        
        with col3:
            if current_idx < len(flashcards) - 1:
                if st.button("Next →", key=f"{key_prefix}_next"):
                    st.session_state[f"{key_prefix}_current_card"] += 1
                    st.rerun()
        
        # Display current card
        card = flashcards[current_idx]
        st.write("#### Question:")
        st.write(card["question"])
        
        # Show/hide answer
        if f"{key_prefix}_show_answer_{current_idx}" not in st.session_state:
            st.session_state[f"{key_prefix}_show_answer_{current_idx}"] = False
        
        if st.button("Show Answer" if not st.session_state[f"{key_prefix}_show_answer_{current_idx}"] 
                     else "Hide Answer", key=f"{key_prefix}_toggle_{current_idx}"):
            st.session_state[f"{key_prefix}_show_answer_{current_idx}"] = not st.session_state[f"{key_prefix}_show_answer_{current_idx}"]
            st.rerun()
        
        if st.session_state[f"{key_prefix}_show_answer_{current_idx}"]:
            st.write("#### Answer:")
            st.write(card["answer"])
    
    with tab2:
        # List view of all cards
        st.write("### All Flashcards")
        
        for i, card in enumerate(flashcards):
            with st.expander(f"Card {i+1}: {card['question'][:50]}..."):
                st.write("**Question:**")
                st.write(card["question"])
                st.write("**Answer:**")
                st.write(card["answer"])

def progress_dashboard(chunks, completed_chunks):
    """
    Display a progress dashboard for learning chunks.
    
    Args:
        chunks (list): List of chunk dictionaries
        completed_chunks (set): Set of indices of completed chunks
    
    Returns:
        None
    """
    st.write("### Learning Progress")
    
    # Overall progress
    total_chunks = len(chunks)
    total_completed = len(completed_chunks)
    
    if total_chunks > 0:
        progress_percentage = (total_completed / total_chunks) * 100
    else:
        progress_percentage = 0
    
    st.progress(progress_percentage / 100)
    st.write(f"Overall Progress: {progress_percentage:.1f}%")
    
    # Calculate estimated time remaining
    total_estimated_time = sum(chunk.get("estimated_time", 0) for chunk in chunks)
    completed_time = sum(chunks[i].get("estimated_time", 0) for i in completed_chunks if i < len(chunks))
    remaining_time = total_estimated_time - completed_time
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Chunks Completed", f"{total_completed}/{total_chunks}")
    with col2:
        st.metric("Estimated Time Total", f"{total_estimated_time} min")
    with col3:
        st.metric("Estimated Time Remaining", f"{remaining_time} min")
    
    # Detailed progress by chunk
    st.write("### Chunk Details")
    
    # Create a DataFrame for better display
    chunk_data = []
    for i, chunk in enumerate(chunks):
        chunk_data.append({
            "Chunk": i + 1,
            "Title": chunk.get("title", f"Chunk {i+1}"),
            "Status": "Completed" if i in completed_chunks else "Pending",
            "Est. Time": f"{chunk.get('estimated_time', 0)} min"
        })
    
    if chunk_data:
        df = pd.DataFrame(chunk_data)
        st.dataframe(df, hide_index=True)

def concept_tree_view(concept_map):
    """
    Display a hierarchical tree view of concepts.
    
    Args:
        concept_map (dict): Concept map data with nodes and edges
    
    Returns:
        None
    """
    if not concept_map or "nodes" not in concept_map or "edges" not in concept_map:
        st.info("No concept map data available.")
        return
    
    st.write("### Concept Hierarchy")
    
    # Build a tree structure from edges
    nodes = concept_map["nodes"]
    edges = concept_map["edges"]
    
    # Find root nodes (nodes with no parents)
    child_nodes = set(edge["target"] for edge in edges)
    root_node_ids = [node["id"] for node in nodes if node["id"] not in child_nodes]
    
    # Build child lookup
    children = {}
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        if source not in children:
            children[source] = []
        children[source].append(target)
    
    # Node lookup
    node_lookup = {node["id"]: node for node in nodes}
    
    # Recursive function to display the tree
    def display_node(node_id, level=0):
        node = node_lookup.get(node_id, {"label": f"Unknown Node {node_id}"})
        indent = "  " * level
        expander_label = f"{indent}{'└─ ' if level > 0 else ''}{node.get('label', node_id)}"
        
        with st.expander(expander_label, expanded=(level < 1)):
            st.write(node.get("description", "No description available."))
            
            if node_id in children:
                for child_id in children[node_id]:
                    display_node(child_id, level + 1)
    
    # Display from root nodes
    for root_id in root_node_ids:
        display_node(root_id)

def summary_tree_view(summaries_tree):
    """
    Display a hierarchical view of summary levels.
    
    Args:
        summaries_tree (list): List of summary level dictionaries
    
    Returns:
        None
    """
    if not summaries_tree:
        st.info("No summary tree available.")
        return
    
    for i, level in enumerate(summaries_tree):
        with st.expander(f"Level {i+1}: {level.get('title', f'Summary Level {i+1}')}", expanded=(i==0)):
            st.write(level.get("content", ""))
            
            # If there are mapped sections, show them
            if "mapped_sections" in level:
                st.write("**Mapped to original text:**")
                for section in level["mapped_sections"]:
                    st.markdown(f"- {section.get('title', 'Section')}")