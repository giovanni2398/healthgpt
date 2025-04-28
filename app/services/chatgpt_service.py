import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from app.config.config import ACCEPTED_INSURANCE_PROVIDERS

load_dotenv()

class ChatGPTService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        
        self.client = OpenAI(api_key=self.api_key)

    def generate_response(self, prompt: str, system_message: str = None) -> str:
        """
        Generate a response using OpenAI's GPT model.
        
        Args:
            prompt (str): The user's message or prompt
            system_message (str, optional): A system message to guide the model's behavior
            
        Returns:
            str: The generated response
            
        Raises:
            Exception: If there's an error calling the OpenAI API
        """
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"Failed to generate response from OpenAI: {str(e)}")

    def analyze_patient_type(self, message: str) -> dict:
        """
        Analyze patient's message to classify insurance/private.
        """
        system_message = """
        You are a medical scheduling assistant. Analyze the patient's message to determine:
        1. If they want to schedule through insurance or as a private patient
        2. If through insurance, identify which insurance provider they mentioned
        3. Your confidence level in this analysis (0.0 to 1.0)

        Respond in JSON format ONLY, without any explanations, like this:
        {
            "type": "insurance" or "private",
            "insurance_name": "name of insurance" or null,
            "confidence": 0.0 to 1.0
        }
        """

        try:
            response = self.generate_response(message, system_message)
            cleaned_response = self.clean_json_response(response)
            return json.loads(cleaned_response)

        except Exception as e:
            raise RuntimeError(f"Failed to analyze patient type: {str(e)}")

    def validate_insurance(self, insurance_name: str) -> bool:
        """
        Validate if an insurance is accepted.
        """
        return insurance_name in ACCEPTED_INSURANCE_PROVIDERS

    @staticmethod
    def clean_json_response(response: str) -> str:
        """Extract JSON from a messy OpenAI response."""
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return match.group(0)
        raise ValueError("No valid JSON found in response.")
