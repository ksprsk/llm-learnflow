# AI-Based Personal Learning Framework

A Streamlit application that leverages AI to enhance learning efficiency, specifically designed for analytical thinkers who prefer structured approaches to learning.

## Core Features

- **Quick Summary + Bidirectional Highlighting**: Generate summaries with interactive highlighting between original text and summary
- **Concept Map Generation + Structure Mapping**: Visualize text structure with connections to original content
- **Progressive Learning Chunks**: Break down documents into logical learning units with estimated time
- **Instant Q&amp;A Mode**: Ask questions while maintaining context
- **Summary Tree View**: Hierarchical visualization of summaries mapped to source text
- **Responsive Dashboard**: Track learning progress and completed chunks
- **Contextual Examples**: Get varied examples for selected concepts
- **Line-by-Line Explanation**: Detailed explanations for sentences, equations, or code
- **Highlight to Flashcard**: Convert highlights to Anki-compatible flashcards

## Setup

1. Clone this repository:
   ```bash
   git clone git@github.com:ksprsk/llm-learnflow.git
   cd llm-learnflow
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Integrated Workflow

1. **Input**: Provide the text you want to learn
2. **Initial Analysis**: AI analyzes text to generate summary, concept map, chunks, and dashboard
3. **Chunk Selection**: Choose a learning chunk to focus on
4. **Learning Tools**: Select text and use toolbar/context menu/shortcuts to access tools
5. **Completion**: Mark chunks as complete and track progress in dashboard
6. **Data Export**: Export generated flashcards to use with external tools like Anki

## Extensibility

The framework is designed with extensibility in mind:
- **Modular Design**: Add new features as independent modules
- **API Adapters**: Easily switch between different LLM providers
- **Configuration Management**: JSON/text-based settings and profile-specific prompts
- **Feature Toggles**: Declaratively control feature activation
- **Hook System**: Insert custom logic at key points
- **CLI Support**: Command-line interface for automation

## Philosophy

- **AI as Assistant**: AI enhances understanding but you remain the learning agent
- **User-Driven**: System responds to explicit requests, minimizing distractions
- **Simplicity &amp; Transparency**: Easy to understand, modify, and extend
- **Progressive Enhancement**: Start simple and add features as needed
