import json
import logging
import requests
import re
from typing import Dict, Any, Optional

class OllamaClient:
    """
    Client for interacting with Ollama API to access local LLMs.
    
    This class provides methods to communicate with locally hosted LLMs through Ollama,
    particularly focused on enhancing prompts for creative applications.
    """
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "deepseek-r1:latest"):
        """
        Initialize the Ollama client.
        
        Args:
            host: The host URL where Ollama is running
            model: The model identifier to use for generations
        """
        self.host = host
        self.model = model
        self.api_endpoint = f"{host}/api/generate"
        
    def enhance_prompt(self, prompt: str) -> str:
        """
        Enhance a basic prompt into a more detailed, creative description.
        
        Args:
            prompt: The original user prompt
            
        Returns:
            str: Enhanced, detailed prompt suitable for image generation
        """
        system_prompt = """You are an expert at creating detailed, vivid descriptions for image generation.
Take the user's basic prompt and enhance it with specific details about:
- Lighting, colors, and atmosphere
- Detailed visual elements
- Style, mood, and artistic direction
Your output should ONLY be the enhanced prompt text, with no explanations or additional text."""

        try:
            prompt_data = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\nUser prompt: {prompt}\n\nEnhanced prompt:",
                "stream": False
            }
            
            logging.info(f"Sending prompt to Ollama: {prompt}")
            response = requests.post(self.api_endpoint, json=prompt_data)
            
            if response.status_code == 200:
                result = response.json()
                enhanced_prompt = result.get("response", "").strip()
                
                # Clean up any thinking text or tags
                enhanced_prompt = self._clean_llm_output(enhanced_prompt)
                
                logging.info(f"Enhanced prompt: {enhanced_prompt}")
                return enhanced_prompt
            else:
                logging.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                return prompt  # Return original prompt on error
                
        except Exception as e:
            logging.error(f"Error enhancing prompt: {str(e)}")
            return prompt  # Return original prompt on error
            
    def generate_creative_prompt(self, user_prompt: str, memory_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a creative, detailed prompt using the LLM, considering memory context if provided.
        
        Args:
            user_prompt: The original prompt from the user
            memory_context: Optional context from previous interactions
            
        Returns:
            Dict with enhanced prompt and additional metadata
        """
        context_text = ""
        if memory_context:
            context_text = f"Consider this context from previous creations: {memory_context}\n\n"
            
        # Use a simpler approach that doesn't require JSON output
        system_prompt = f"""You are a creative AI assisting with generating detailed descriptions for visual content.
{context_text}The user wants to create: {user_prompt}

Please enhance this prompt with specific details about:
1. Visual details (colors, lighting, composition)
2. Style references
3. Mood and atmosphere

Your output should be ONLY the enhanced, detailed description with no explanations or additional text.
"""

        try:
            prompt_data = {
                "model": self.model,
                "prompt": system_prompt,
                "stream": False
            }
            
            response = requests.post(self.api_endpoint, json=prompt_data)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                
                # Clean up the response
                enhanced_prompt = self._clean_llm_output(response_text)
                
                # Extract style and mood manually
                style_tags = self._extract_style_tags(enhanced_prompt)
                mood = self._extract_mood(enhanced_prompt)
                
                return {
                    "enhanced_prompt": enhanced_prompt,
                    "style_tags": style_tags,
                    "mood": mood
                }
            else:
                logging.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                return {
                    "enhanced_prompt": user_prompt,
                    "style_tags": [],
                    "mood": "unknown"
                }
                
        except Exception as e:
            logging.error(f"Error generating creative prompt: {str(e)}")
            return {
                "enhanced_prompt": user_prompt,
                "style_tags": [],
                "mood": "unknown"
            }
    
    def _clean_llm_output(self, text: str) -> str:
        """
        Clean up model output to remove thinking text and XML-like tags.
        
        Args:
            text: The raw output from the LLM
            
        Returns:
            str: Cleaned output text
        """
        # Remove thinking sections
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # Remove other XML-like tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove lines with "enhanced prompt:"
        lines = text.split('\n')
        filtered_lines = [line for line in lines if not line.lower().startswith('enhanced prompt:')]
        text = '\n'.join(filtered_lines)
        
        return text.strip()
    
    def _extract_style_tags(self, text: str) -> list:
        """Extract potential style tags from the text"""
        # List of common art styles and descriptors
        styles = [
            "realistic", "abstract", "impressionist", "surreal", "minimalist", 
            "cartoon", "anime", "fantasy", "sci-fi", "vintage", "modern", 
            "cyberpunk", "steampunk", "gothic", "noir", "watercolor", "oil painting",
            "sketch", "digital art", "pop art", "conceptual", "futuristic"
        ]
        
        found_styles = []
        for style in styles:
            if style in text.lower():
                found_styles.append(style)
                
        return found_styles
    
    def _extract_mood(self, text: str) -> str:
        """Extract potential mood from the text"""
        # List of common moods
        moods = [
            "happy", "sad", "mysterious", "dark", "light", "joyful", "melancholic",
            "serene", "chaotic", "peaceful", "tense", "nostalgic", "dreamy",
            "nightmare", "fantasy", "romantic", "scary", "horror", "whimsical",
            "dramatic", "epic", "tranquil", "energetic", "calm", "angry"
        ]
        
        for mood in moods:
            if mood in text.lower():
                return mood
                
        return "unknown" 