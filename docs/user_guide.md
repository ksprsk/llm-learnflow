# AI Learning Framework User Guide

## Introduction

Welcome to the AI Learning Framework, designed to help analytical thinkers maximize learning efficiency through AI-enhanced tools and structured approaches.

## Getting Started

1. **Installation**
   - Clone the repository
   - Install requirements with `pip install -r requirements.txt`
   - Create a `.env` file with your OpenAI API key
   - Run with `streamlit run app.py`

2. **Input Methods**
   - Text input: Paste text directly into the text area
   - File upload: Upload text, markdown, or code files

## Core Features

### Text Analysis

After you submit text, the system will automatically:
- Generate a concise summary
- Create a concept map of key ideas and relationships
- Divide content into logical learning chunks
- Build a hierarchical summary tree
- Set up a learning dashboard

### Learning Tools

While studying each chunk, you can use these tools:

1. **Instant Q&amp;A**
   - Ask specific questions about the content
   - Receive concise, context-aware answers

2. **Line-by-Line Explanation**
   - Select difficult sentences, equations, or code
   - Get detailed breakdowns of meaning and structure

3. **Contextual Examples**
   - Request varied examples for any concept
   - Choose from code, analogies, real-life applications, etc.

4. **Flashcard Creation**
   - Select important text to convert to flashcards
   - Export in Anki-compatible format for later review

### Navigation and Progress Tracking

- **Chunk Navigation**: Move between learning chunks via the sidebar
- **Progress Tracking**: Mark chunks as complete to track your progress
- **Dashboard**: View overall learning progress and estimated time

## Advanced Usage

### Highlighting Features

- **Bidirectional Highlighting**: Find connections between original text and summary
- **Concept Highlighting**: Highlight specific terms to see their occurrences

### Summary Tree View

The Summary Tree provides multiple levels of abstraction:
- Level 1: Highest-level summary
- Level 2: More detailed summary
- Level 3: Comprehensive overview with mappings to original text

### Exporting Data

- **Flashcards**: Export as CSV for Anki import
- **Summaries**: Download for later reference

## Tips for Effective Use

1. **Start with the Summary**: Get a high-level overview before diving into chunks
2. **Use the Concept Map**: Understand relationships between ideas
3. **Learn Progressively**: Work through chunks in order
4. **Ask Questions**: Use the Q&amp;A tool whenever you're confused
5. **Create Flashcards**: Mark key information for later review
6. **Check the Dashboard**: Monitor your overall progress

## Troubleshooting

- **API Errors**: Check your API key in the .env file
- **Long Processing Times**: Large texts may take longer to process
- **Text Formatting Issues**: Try different input formats if you encounter problems

## Extending the Framework

The framework is designed to be extensible:
- Add new plugins in the `plugins/` directory
- Modify prompt templates in the `prompts/` directory
- Add custom hooks in `hooks.py`
- Create new API adapters in the `adapters/` directory

For more information, see the README.md and code documentation.