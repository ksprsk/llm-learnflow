import os
import time
import json
import openai
import hooks
from pathlib import Path

class AIAdapter:
    """Universal adapter for multiple AI models."""
    
    def __init__(self, config_path="key.json", model_name=None):
        """
        Initialize the AI adapter with configuration from a JSON file.
        
        Args:
            config_path (str): Path to the configuration JSON file
            model_name (str, optional): Name of the specific model to use from config
        """
        # Load configuration
        self.config = self._load_config(config_path)
        self.models = {}
        
        # Initialize all models from config or select one specific model
        for model_config in self.config.get("models", []):
            model_instance = self._create_model_instance(model_config)
            self.models[model_config["name"]] = model_instance
            
        # Set the active model (either specified or first in config)
        if model_name and model_name in self.models:
            self.active_model = self.models[model_name]
        elif self.models:
            self.active_model = next(iter(self.models.values()))
        else:
            raise ValueError("No models configured")
    
    def _load_config(self, config_path):
        """Load configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading configuration: {str(e)}")
            return {"models": []}
    
    def _create_model_instance(self, model_config):
        """Create an instance of AIModel from configuration."""
        return AIModel(
            name=model_config.get("name", "Default"),
            model_name=model_config.get("model_name", "gpt-4"),
            api_key=model_config.get("api_key"),
            base_url=model_config.get("base_url"),
            max_completion_tokens=model_config.get("max_completion_tokens", 1000),
            extra_body=model_config.get("extra_body", {})
        )
    
    def set_active_model(self, model_name):
        """Set the active model by name."""
        if model_name in self.models:
            self.active_model = self.models[model_name]
            return True
        return False
    
    def generate_completion(self, prompt, temperature=0.7, stream=False):
        """
        Generate a text completion using the active AI model.
        
        Args:
            prompt (str): The prompt to generate completion for
            temperature (float, optional): Sampling temperature. Defaults to 0.7.
            stream (bool, optional): Whether to stream the response. Defaults to False.
        
        Returns:
            str: The generated completion
        """
        messages = [{"role": "user", "content": prompt}]
        return self.active_model.generate_response(messages)
    
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


class AIModel:
    def __init__(self, name, model_name, api_key, base_url=None, max_completion_tokens=1000, extra_body=None):
        """
        Initialize an AI model client.
        
        Args:
            name (str): Display name for the model
            model_name (str): Name of the model to use with the API
            api_key (str): API key for authentication
            base_url (str, optional): Base URL for the API
            max_completion_tokens (int, optional): Maximum tokens in completion
            extra_body (dict, optional): Additional parameters for the request
        """
        self.name = name
        self.model_name = model_name
        self.api_key = api_key
        self.max_completion_tokens = max_completion_tokens
        self.extra_body = extra_body or {}
        
        # Initialize the client
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = openai.OpenAI(**client_kwargs)
    
    def generate_response(self, messages):
        """
        Generate a response based on the message history.
        
        Args:
            messages (list): List of message dictionaries with role and content
            
        Returns:
            str: Generated response from the AI model
        """
        # Transform messages for API compatibility
        api_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                # Keep system messages as is
                api_messages.append(msg)
            elif msg["role"] == self.name:
                # Messages from this model become assistant messages
                api_messages.append({
                    "role": "assistant",
                    "content": msg["content"]
                })
            else:
                # Messages from other sources (user or other models) become user messages
                # with the source prepended to the content
                source = msg["role"]
                content = msg["content"]
                
                # Only prepend source if it's not already there
                if not content.startswith(f"{source}:"):
                    content = f"{source}: {content}"
                
                api_messages.append({
                    "role": "user",
                    "content": content
                })
        
        # Create the completion request
        kwargs = {
            "model": self.model_name,
            "messages": api_messages,
            "max_tokens": self.max_completion_tokens,
        }
        
        # Add any additional parameters if provided
        if self.extra_body:
            kwargs.update(self.extra_body)
        
        try:
            # Generate completion
            completion = self.client.chat.completions.create(**kwargs)
            
            # Return the generated content
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error generating response from {self.name}: {str(e)}")
            return f"[Error] Failed to generate response: {str(e)}"