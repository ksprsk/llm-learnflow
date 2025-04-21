import streamlit as st
import os
import json
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Local imports
from adapters.openai_adapter import AIAdapter
from utils import (
    process_text,
    generate_chunks,
    highlight_text,
    count_tokens,
    create_concept_map,
    convert_to_flashcards
)
import widgets
import hooks

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="AI Learning Framework",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
@st.cache_resource
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()

# Initialize API adapter
api_adapter = AIAdapter("key.json", "Gemini")


# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_text = ""
    st.session_state.summary = ""
    st.session_state.chunks = []
    st.session_state.concept_map = {}
    st.session_state.current_chunk_index = None
    st.session_state.completed_chunks = set()
    st.session_state.flashcards = []
    st.session_state.questions_history = []
    st.session_state.summaries_tree = []

# Add custom CSS
st.markdown("""
<style>
    .highlight { background-color: rgba(255, 255, 0, 0.3); }
    .completed { background-color: rgba(0, 255, 0, 0.1); }
    .concept-node { border: 1px solid #ddd; padding: 10px; border-radius: 5px; }
    .stButton button {width: 100%;}
    .line-highlight {background-color: #f0f8ff; padding: 5px; border-left: 3px solid #4361ee;}
    
    /* Improve readability of text in main panel */
    .main-text {
        line-height: 1.6;
        font-size: 1.1rem;
    }
    
    /* Style for flashcards */
    .flashcard {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Style for dashboard panels */
    .dashboard-panel {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Trigger hooks.on_app_load()
hooks.on_app_load()

# Sidebar
with st.sidebar:
    st.title("Learning Framework")
    
    # Input section
    st.header("Input Text")
    
    # Input method selection
    input_method = st.radio("Choose input method:", ["Text Input", "File Upload"])
    
    if input_method == "Text Input":
        user_text = st.text_area("Enter text to learn:", height=200)
        if st.button("Process Text") and user_text.strip():
            st.session_state.current_text = user_text
            with st.spinner("Processing text..."):
                # Process text
                summary, chunks, concept_map = process_text(user_text, api_adapter)
                st.session_state.summary = summary
                st.session_state.chunks = chunks
                st.session_state.concept_map = concept_map
                st.session_state.current_chunk_index = 0
                
                # Generate summary tree
                st.session_state.summaries_tree = api_adapter.generate_summary_tree(user_text)
            st.success("Text processed successfully!")
            st.rerun()
    
    else:  # File Upload
        uploaded_file = st.file_uploader("Choose a text file", type=["txt", "md", "py", "java", "js", "html", "css"])
        if uploaded_file is not None:
            user_text = uploaded_file.read().decode("utf-8")
            st.session_state.current_text = user_text
            with st.spinner("Processing text..."):
                # Process text
                summary, chunks, concept_map = process_text(user_text, api_adapter)
                st.session_state.summary = summary
                st.session_state.chunks = chunks
                st.session_state.concept_map = concept_map
                st.session_state.current_chunk_index = 0
                
                # Generate summary tree
                st.session_state.summaries_tree = api_adapter.generate_summary_tree(user_text)
            st.success("File processed successfully!")
            st.rerun()
    
    # Display chunk navigation if text has been processed
    if st.session_state.chunks:
        st.header("Learning Chunks")
        
        # Show chunk list with completion status
        for i, chunk in enumerate(st.session_state.chunks):
            chunk_title = f"Chunk {i+1}: {chunk['title']}"
            is_completed = i in st.session_state.completed_chunks
            chunk_status = "✅ " if is_completed else "📝 "
            
            if st.button(f"{chunk_status} {chunk_title}", key=f"chunk_{i}"):
                st.session_state.current_chunk_index = i
                st.rerun()
        
        # Progress tracker
        progress = len(st.session_state.completed_chunks) / len(st.session_state.chunks)
        st.progress(progress)
        st.write(f"Progress: {int(progress * 100)}% completed")

# Main content area
if not st.session_state.current_text:
    # Welcome screen
    st.title("AI-Based Personal Learning Framework")
    st.write("""
    Welcome to your AI-enhanced learning assistant, designed to maximize efficiency for analytical learners.
    
    ### Getting Started
    1. Input the text you want to learn through the sidebar
    2. The AI will analyze and structure the content for optimal learning
    3. Navigate through chunks and use the tools to enhance your understanding
    
    ### Key Features
    - **Quick Summaries with Bidirectional Highlighting**
    - **Automated Concept Mapping with Structure Analysis**
    - **Progressive Learning with Logical Chunks**
    - **Contextual Q&amp;A and Examples**
    - **Flashcard Creation from Highlights**
    """)
    
    # Sample text button
    if st.button("Try with Sample Text"):
        try:
            with open("examples/sample_text.txt", "r") as f:
                sample_text = f.read()
                st.session_state.current_text = sample_text
                with st.spinner("Processing sample text..."):
                    summary, chunks, concept_map = process_text(sample_text, api_adapter)
                    st.session_state.summary = summary
                    st.session_state.chunks = chunks
                    st.session_state.concept_map = concept_map
                    st.session_state.current_chunk_index = 0
                    
                    # Generate summary tree
                    st.session_state.summaries_tree = api_adapter.generate_summary_tree(sample_text)
                st.success("Sample text processed!")
                st.rerun()
        except Exception as e:
            st.error(f"Error loading sample text: {str(e)}")

else:
    # Text has been processed, show learning interface
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Learning", "Summary", "Concept Map", "Summary Tree", "Dashboard"])
    
    with tab1:
        # Learning tab
        if st.session_state.current_chunk_index is not None:
            current_chunk = st.session_state.chunks[st.session_state.current_chunk_index]
            
            # Chunk header
            st.header(f"Chunk {st.session_state.current_chunk_index + 1}: {current_chunk['title']}")
            st.write(f"Estimated learning time: {current_chunk['estimated_time']} minutes")
            
            # Mark as complete button
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.session_state.current_chunk_index in st.session_state.completed_chunks:
                    if st.button("Mark as Incomplete"):
                        st.session_state.completed_chunks.remove(st.session_state.current_chunk_index)
                        st.rerun()
                else:
                    if st.button("Mark as Complete"):
                        st.session_state.completed_chunks.add(st.session_state.current_chunk_index)
                        st.rerun()
            
            # Chunk content
            st.markdown("---")
            st.markdown(f'<div class="main-text">{current_chunk["content"]}</div>', unsafe_allow_html=True)
            st.markdown("---")
            
            # Tools section
            st.subheader("Learning Tools")
            
            tools_col1, tools_col2 = st.columns(2)
            
            with tools_col1:
                # Q&amp;A Tool
                with st.expander("💬 Ask a Question", expanded=True):
                    question = st.text_input("Your question about this chunk:", key="question_input")
                    if st.button("Get Answer", key="ask_button"):
                        with st.spinner("Generating answer..."):
                            try:
                                context = current_chunk['content']
                                answer = api_adapter.ask_question(question, context)
                                
                                # Add to history
                                st.session_state.questions_history.append({
                                    "question": question,
                                    "answer": answer,
                                    "chunk_index": st.session_state.current_chunk_index,
                                    "timestamp": time.time()
                                })
                                
                                # Display answer
                                st.write("### Answer")
                                st.markdown(f'<div class="line-highlight">{answer}</div>', unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error generating answer: {str(e)}")
                
                # Line Explanation Tool
                with st.expander("📝 Line-by-Line Explanation"):
                    line_to_explain = st.text_area("Paste text for detailed explanation:", height=100)
                    if st.button("Explain"):
                        with st.spinner("Generating explanation..."):
                            try:
                                explanation = api_adapter.explain_line(line_to_explain, current_chunk['content'])
                                st.write("### Explanation")
                                st.markdown(f'<div class="line-highlight">{explanation}</div>', unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error generating explanation: {str(e)}")
            
            with tools_col2:
                # Contextual Examples Tool
                with st.expander("🔍 Get Contextual Examples", expanded=True):
                    concept = st.text_input("Concept or term you want examples for:")
                    example_types = st.multiselect(
                        "Example types:",
                        ["Code", "Analogy", "Real-life", "Visual", "Historical"],
                        default=["Analogy", "Real-life"]
                    )
                    if st.button("Generate Examples"):
                        with st.spinner("Generating examples..."):
                            try:
                                examples = api_adapter.generate_examples(concept, example_types, current_chunk['content'])
                                st.write("### Examples")
                                st.markdown(f'<div class="line-highlight">{examples}</div>', unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error generating examples: {str(e)}")
                
                # Flashcard Creation Tool
                with st.expander("📇 Create Flashcards"):
                    flashcard_text = st.text_area("Enter text to convert to flashcards:", height=100)
                    if st.button("Generate Flashcards"):
                        with st.spinner("Creating flashcards..."):
                            try:
                                new_flashcards = convert_to_flashcards(flashcard_text, api_adapter)
                                st.session_state.flashcards.extend(new_flashcards)
                                
                                # Display created flashcards
                                st.write("### Created Flashcards")
                                for i, card in enumerate(new_flashcards):
                                    st.markdown(f'<div class="flashcard">', unsafe_allow_html=True)
                                    st.write(f"**Q: {card['question']}**")
                                    with st.expander("Show Answer"):
                                        st.write(card['answer'])
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
                                st.success(f"Created {len(new_flashcards)} flashcards successfully!")
                            except Exception as e:
                                st.error(f"Error creating flashcards: {str(e)}")
    
    with tab2:
        # Summary tab
        st.header("Text Summary")
        if st.session_state.summary:
            # Display summary with highlighting option
            st.markdown(f'<div class="main-text">{st.session_state.summary}</div>', unsafe_allow_html=True)
            
            # Option to export summary
            if st.button("Export Summary"):
                summary_data = st.session_state.summary
                st.download_button(
                    label="Download Summary",
                    data=summary_data,
                    file_name=f"summary_{uuid.uuid4().hex[:8]}.txt",
                    mime="text/plain"
                )
            
            # Bidirectional highlighting controls
            st.subheader("Bidirectional Highlighting")
            highlight_term = st.text_input("Enter term to highlight in both summary and original text:")
            if highlight_term and st.button("Highlight Term"):
                # Re-render the summary with highlighted term
                highlighted_summary = highlight_text(st.session_state.summary, [highlight_term])
                st.markdown(f'<div class="main-text">{highlighted_summary}</div>', unsafe_allow_html=True)
                
                # Find and display matching text in original
                if st.session_state.current_chunk_index is not None:
                    current_chunk = st.session_state.chunks[st.session_state.current_chunk_index]
                    highlighted_chunk = highlight_text(current_chunk['content'], [highlight_term])
                    st.subheader("Matching Content in Current Chunk")
                    st.markdown(f'<div class="main-text">{highlighted_chunk}</div>', unsafe_allow_html=True)
    
    with tab3:
        # Concept Map tab
        st.header("Concept Map")
        if st.session_state.concept_map:
            st.info("Below is a simplified representation of the concept map. In a complete implementation, this would be an interactive visualization.")
            
            # Create a simple visualization of the concept map
            if "nodes" in st.session_state.concept_map and "edges" in st.session_state.concept_map:
                # Display main concepts
                st.subheader("Main Concepts")
                for node in st.session_state.concept_map["nodes"]:
                    with st.expander(f"{node.get('label', 'Concept')}"):
                        st.write(node.get("description", "No description available"))
                        
                        # Find related concepts
                        related = []
                        for edge in st.session_state.concept_map["edges"]:
                            if edge["source"] == node["id"]:
                                target_node = next((n for n in st.session_state.concept_map["nodes"] if n["id"] == edge["target"]), None)
                                if target_node:
                                    related.append((target_node.get("label", "Related concept"), edge.get("label", "relates to")))
                        
                        if related:
                            st.write("**Related Concepts:**")
                            for rel_concept, relation in related:
                                st.write(f"- {rel_concept} ({relation})")
            else:
                st.json(st.session_state.concept_map)
    
    with tab4:
        # Summary Tree View tab
        st.header("Summary Tree View")
        if st.session_state.summaries_tree:
            for i, level in enumerate(st.session_state.summaries_tree):
                st.subheader(f"Level {i+1}: {level.get('title', f'Summary Level {i+1}')}")
                st.markdown(f'<div class="main-text">{level.get("content", "")}</div>', unsafe_allow_html=True)
                
                # If there are mapped sections, show them
                if "mapped_sections" in level:
                    with st.expander("View mapped sections in original text"):
                        for section in level["mapped_sections"]:
                            st.markdown(f"**{section.get('title', 'Section')}**")
                            st.markdown(f'<div class="line-highlight">{section.get("content", "")}</div>', unsafe_allow_html=True)
                
                st.markdown("---")
        else:
            st.info("Summary tree not available. Generate a summary first.")
    
    with tab5:
        # Dashboard tab
        st.header("Learning Dashboard")
        
        # Progress overview
        total_chunks = len(st.session_state.chunks)
        completed_chunks = len(st.session_state.completed_chunks)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Chunks", total_chunks)
        with col2:
            st.metric("Completed", completed_chunks)
        with col3:
            if total_chunks > 0:
                completion_percentage = int((completed_chunks / total_chunks) * 100)
            else:
                completion_percentage = 0
            st.metric("Completion", f"{completion_percentage}%")
        
        # Progress bar
        if total_chunks > 0:
            st.progress(completed_chunks / total_chunks)
        
        # Estimated time tracking
        total_time = sum(chunk.get("estimated_time", 0) for chunk in st.session_state.chunks)
        completed_time = sum(st.session_state.chunks[i].get("estimated_time", 0) for i in st.session_state.completed_chunks if i < total_chunks)
        remaining_time = total_time - completed_time
        
        st.markdown(f'<div class="dashboard-panel">', unsafe_allow_html=True)
        st.subheader("Time Tracking")
        time_col1, time_col2, time_col3 = st.columns(3)
        with time_col1:
            st.metric("Total Time", f"{total_time} min")
        with time_col2:
            st.metric("Completed", f"{completed_time} min")
        with time_col3:
            st.metric("Remaining", f"{remaining_time} min")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Flashcards Overview
        st.markdown(f'<div class="dashboard-panel">', unsafe_allow_html=True)
        st.subheader("Flashcards")
        st.write(f"Total flashcards created: {len(st.session_state.flashcards)}")
        
        if st.session_state.flashcards:
            if st.button("Export Flashcards (Anki CSV)"):
                # Create CSV content for Anki import
                csv_content = "question,answer\n"
                for card in st.session_state.flashcards:
                    # Escape quotes and format as CSV
                    question = card['question'].replace('"', '""')
                    answer = card['answer'].replace('"', '""')
                    csv_content += f'"{question}","{answer}"\n'
                
                # Provide download button
                st.download_button(
                    label="Download Anki CSV",
                    data=csv_content,
                    file_name=f"flashcards_{uuid.uuid4().hex[:8]}.csv",
                    mime="text/csv"
                )
            
            # Show sample flashcards
            with st.expander("View Flashcards"):
                widgets.flashcard_viewer(st.session_state.flashcards)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Q&amp;A History
        st.markdown(f'<div class="dashboard-panel">', unsafe_allow_html=True)
        st.subheader("Questions Asked")
        if st.session_state.questions_history:
            for i, qa in enumerate(st.session_state.questions_history):
                with st.expander(f"Q: {qa['question']}"):
                    st.write("**Answer:**")
                    st.write(qa['answer'])
                    st.write(f"*From Chunk {qa['chunk_index'] + 1}*")
        else:
            st.write("No questions asked yet.")
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "AI Learning Framework | [Documentation](https://github.com/yourusername/ai-learning-framework) | "
    "Created for analytical learners seeking extreme learning efficiency"
)

# Trigger hooks.on_app_close() when appropriate
hooks.on_app_close()
