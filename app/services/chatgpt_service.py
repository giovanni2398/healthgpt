import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
from app.config.config import OPENAI_API_KEY, OPENAI_MODEL

class ChatGPTService:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL

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
            raise Exception(f"Error generating response: {str(e)}")

    def analyze_patient_type(self, message: str) -> dict:
        """
        Analyze a patient's message to determine if they want to schedule through insurance or private.
        
        Args:
            message (str): The patient's message
            
        Returns:
            dict: A dictionary containing the analysis results
                {
                    "type": "insurance" | "private",
                    "insurance_name": str | None,
                    "confidence": float
                }
        """
        system_message = """
        You are a medical scheduling assistant. Analyze the patient's message to determine:
        1. If they want to schedule through insurance or as a private patient
        2. If through insurance, identify which insurance provider they mentioned
        3. Your confidence level in this analysis (0.0 to 1.0)
        
        Respond in JSON format only with the following structure:
        {
            "type": "insurance" or "private",
            "insurance_name": "name of insurance" or null,
            "confidence": 0.0 to 1.0
        }
        """
        
        try:
            response = self.generate_response(message, system_message)
            # The response should be a JSON string
            import json
            return json.loads(response)
        except Exception as e:
            raise Exception(f"Error analyzing patient type: {str(e)}")

    def validate_insurance(self, insurance_name: str) -> bool:
        """
        Validate if an insurance provider is accepted by the clinic.
        
        Args:
            insurance_name (str): The name of the insurance provider
            
        Returns:
            bool: True if the insurance is accepted, False otherwise
        """
        from app.config.config import ACCEPTED_INSURANCE_PROVIDERS
        return insurance_name in ACCEPTED_INSURANCE_PROVIDERS
