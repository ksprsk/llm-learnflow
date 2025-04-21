import os
import time
import json
import openai
import hooks

class OpenAIAdapter:
    """Adapter for the OpenAI API."""
    
    def __init__(self, api_key=None, model="gpt-4", max_tokens=1000):
        """
        Initialize the OpenAI adapter.
        
        Args:
            api_key (str, optional): OpenAI API key. Defaults to None.
            model (str, optional): Model to use. Defaults to "gpt-4".
            max_tokens (int, optional): Maximum tokens for completions. Defaults to 1000.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model = model
        self.max_tokens = max_tokens
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_completion(self, prompt, temperature=0.7, stream=False):
        """
        Generate a text completion using the OpenAI API.
        
        Args:
            prompt (str): The prompt to generate completion for
            temperature (float, optional): Sampling temperature. Defaults to 0.7.
            stream (bool, optional): Whether to stream the response. Defaults to False.
        
        Returns:
            str: The generated completion
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=self.max_tokens,
                stream=stream
            )
            
            if stream:
                # Handle streaming response
                collected_chunks = []
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        collected_chunks.append(chunk.choices[0].delta.content)
                        yield chunk.choices[0].delta.content
                return "".join(collected_chunks)
            else:
                # Handle regular response
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            print(f"Error generating completion: {str(e)}")
            raise
    
    def ask_question(self, question, context, temperature=0.7):
        """
        Generate an answer to a question given a context.
        
        Args:
            question (str): The question to answer
            context (str): The context to use for answering
            temperature (float, optional): Sampling temperature. Defaults to 0.7.
        
        Returns:
            str: The generated answer
        """
        prompt = f"""
Given the following context, please answer the question clearly and concisely.
Only use information from the provided context. If you can't answer based on
the context, say "I don't have enough information to answer this question."

Context:
{context}

Question:
{question}

Answer:
"""
        # Get response and apply hooks
        answer = self.generate_completion(prompt, temperature)
        question, answer = hooks.on_qa_generate(question, answer)
        return answer
    
    def explain_line(self, line, context=None, temperature=0.7):
        """
        Generate an explanation for a line of text.
        
        Args:
            line (str): The line to explain
            context (str, optional): Additional context. Defaults to None.
            temperature (float, optional): Sampling temperature. Defaults to 0.7.
        
        Returns:
            str: The generated explanation
        """
        if context:
            prompt = f"""
Provide a detailed explanation of the following line, using the context provided.
Focus on making the explanation extremely clear and analytical.

Context:
{context}

Line to explain:
{line}

Your explanation should cover:
1. The meaning of the line
2. Key concepts or terms
3. How it relates to the broader context
4. Any implicit assumptions or implications

Explanation:
"""
        else:
            prompt = f"""
Provide a detailed explanation of the following line:
Focus on making the explanation extremely clear and analytical.

{line}

Your explanation should cover:
1. The meaning of the line
2. Key concepts or terms
3. Any implicit assumptions or implications
4. Examples that clarify the concept (if relevant)

Explanation:
"""
        return self.generate_completion(prompt, temperature)
    
    def generate_examples(self, concept, example_types, context=None, temperature=0.7):
        """
        Generate examples for a concept.
        
        Args:
            concept (str): The concept to generate examples for
            example_types (list): List of example types to generate
            context (str, optional): Additional context. Defaults to None.
            temperature (float, optional): Sampling temperature. Defaults to 0.7.
        
        Returns:
            str: The generated examples
        """
        example_types_str = ", ".join(example_types)
        
        if context:
            prompt = f"""
Generate concrete examples for the concept "{concept}" based on the following context.
Provide these types of examples: {example_types_str}

Context:
{context}

For each example type, provide 1-2 clear, specific examples that would help an analytical
learner deeply understand the concept. Structure your response with clear headings for
each example type.

Examples:
"""
        else:
            prompt = f"""
Generate concrete examples for the concept "{concept}".
Provide these types of examples: {example_types_str}

For each example type, provide 1-2 clear, specific examples that would help an analytical
learner deeply understand the concept. Structure your response with clear headings for
each example type.

Examples:
"""
        return self.generate_completion(prompt, temperature)
    
    def generate_summary_tree(self, text, levels=3, temperature=0.5):
        """
        Generate a hierarchical summary tree with multiple levels of abstraction.
        
        Args:
            text (str): The text to summarize
            levels (int, optional): Number of summary levels. Defaults to 3.
            temperature (float, optional): Sampling temperature. Defaults to 0.5.
        
        Returns:
            list: List of summary levels with mappings to original text
        """
        prompt = f"""
Create a hierarchical summary tree for the following text, with {levels} levels of abstraction.
Level 1 should be the most concise, high-level summary.
Each subsequent level should add more detail, with the final level containing comprehensive coverage.

For each level, provide:
1. A title for the summary level
2. The summary content
3. Mappings to sections in the original text

Return your response as a JSON array with each level having this structure:
[
  {{
    "title": "Level 1: Executive Summary",
    "content": "The concise level 1 summary...",
    "mapped_sections": [
      {{ "title": "Section title", "content": "Original text excerpt" }}
    ]
  }},
  // Additional levels...
]

Original text:
{text}

JSON response:
"""
        try:
            summary_tree_json = self.generate_completion(prompt, temperature)
            summary_tree = json.loads(summary_tree_json)
            return summary_tree
        except json.JSONDecodeError:
            # Fallback in case of JSON parsing error
            return [
                {
                    "title": "Summary",
                    "content": "Failed to generate hierarchical summary. Please try again.",
                    "mapped_sections": []
                }
            ]
        except Exception as e:
            print(f"Error generating summary tree: {str(e)}")
            return []