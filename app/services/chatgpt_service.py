import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from app.config.config import ACCEPTED_INSURANCE_PROVIDERS
from datetime import datetime

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

    def filter_slots_by_preference(
        self, user_message: str, available_slots: list
    ) -> list:
        """
        Uses ChatGPT to filter a list of available time slots based on user's natural language preference.

        Args:
            user_message (str): The user's message describing their preference (e.g., "amanhã de manhã").
            available_slots (list): A list of dictionaries, where each dict represents a slot
                                    (e.g., {'slot_id': 'xyz', 'start_time': 'YYYY-MM-DDTHH:MM:SS'}).

        Returns:
            list: A (potentially empty) list containing only the slots that match the preference,
                  maintaining the original dictionary structure for each slot.
                  Returns an empty list if filtering fails, is not possible, or no slots match.
        """
        if not available_slots:
            return [] # Nothing to filter

        # 1. Format available slots for the prompt
        formatted_slots_str = "\n".join(
            [f"- ID: {slot['slot_id']} Time: {slot['start_time']}" for slot in available_slots]
        )

        # 2. Define the system message
        system_message = f"""
You are an intelligent assistant helping a user filter available appointment slots based on their preference.
You will be given the user's preference message and a list of available slots with their IDs and ISO 8601 start times.
Analyze the user's preference considering dates (today, tomorrow, specific days like 'terça', 'dia 15'), time of day (morning, afternoon, specific hours like '10h', 'depois das 14h'), and relative terms.
The current date and time context is important for relative terms like 'hoje' or 'amanhã'. Assume current date is {datetime.now().strftime('%Y-%m-%d')} and time is {datetime.now().strftime('%H:%M')} (America/Sao_Paulo time).

Your task is to return ONLY a JSON list containing the exact 'slot_id' strings of the slots from the list below that strictly match the user's preference.

Available Slots:
{formatted_slots_str}

Rules:
- Return ONLY a valid JSON list of strings (slot IDs, e.g., ["slot1", "slot_xyz"]).
- If the user's preference is vague or implies flexibility (e.g., "qualquer horário", "pode ser"), return the IDs of ALL available slots.
- If the user's preference does not match ANY available slots, return an empty JSON list [].
- If you cannot confidently determine matching slots based on the preference and the list, return an empty JSON list [].
- Do not include any explanations, introductory text, apologies, or formatting like ```json. Just the raw JSON list.
- Interpret times relative to the America/Sao_Paulo timezone.
- Assume 'morning' (manhã) is before 12:00, 'afternoon' (tarde) is from 12:00 to 18:00, 'evening/night' (noite) is after 18:00.
"""

        # 3. Define the user prompt for the filtering task
        user_prompt = f"User preference: \"{user_message}\". Please return the JSON list of matching slot IDs from the available list provided in the system message."

        print(f"[ChatGPTService] Filtering slots based on: '{user_message}'")
        # print(f"[ChatGPTService] Prompt being sent to OpenAI:\nSystem: {system_message}\nUser: {user_prompt}") # Optional: Uncomment for debugging prompt

        try:
            # 4. Call OpenAI API
            # Using a model fine-tuned for JSON output might be better, but standard models work with clear instructions.
            # Max tokens might need adjustment based on the number of slots. JSON list of IDs shouldn't be too long usually.
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2, # Lower temperature for more deterministic filtering
                max_tokens=500, # Estimate max tokens needed for a list of IDs
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                response_format={ "type": "json_object"} # Request JSON output if model supports it
            )
            raw_response_content = response.choices[0].message.content.strip()
            print(f"[ChatGPTService] Raw response content from OpenAI: {raw_response_content}")

            # 5. Parse the response (expecting a JSON object possibly containing a list)
            try:
                # Attempt to parse the response as JSON
                parsed_json = json.loads(raw_response_content)

                # The model might return {"slot_ids": [...]}. Extract the list.
                # Handle cases where it might return just the list directly (less common with json_object mode)
                if isinstance(parsed_json, list):
                    matching_slot_ids = parsed_json
                elif isinstance(parsed_json, dict) and isinstance(parsed_json.get("slot_ids"), list):
                    matching_slot_ids = parsed_json["slot_ids"]
                elif isinstance(parsed_json, dict) and isinstance(parsed_json.get("ids"), list):
                    matching_slot_ids = parsed_json["ids"] # Handle another common key
                else:
                    print("[ChatGPTService] JSON response did not contain a recognized list of slot IDs. Assuming no match.")
                    return []

                # Validate that it's a list of strings
                if not all(isinstance(sid, str) for sid in matching_slot_ids):
                    print("[ChatGPTService] Parsed JSON list contains non-string elements. Returning empty list.")
                    return []

            except json.JSONDecodeError:
                print(f"[ChatGPTService] OpenAI response was not valid JSON: {raw_response_content}. Returning empty list.")
                return [] # Failed to parse JSON

            # 6. Filter the original available_slots list based on the returned IDs
            if not matching_slot_ids:
                print("[ChatGPTService] OpenAI returned no matching slots.")
                return []

            # Create a set for efficient lookup
            matching_id_set = set(matching_slot_ids)

            filtered_list = [slot for slot in available_slots if slot['slot_id'] in matching_id_set]

            print(f"[ChatGPTService] Successfully filtered. Matched IDs: {matching_slot_ids}. Returning {len(filtered_list)} slots.")
            return filtered_list

        except Exception as e:
            # 6. Handle errors gracefully
            print(f"[ChatGPTService] Error during slot filtering API call or processing: {e}. Returning empty list.")
            return [] # Return empty list on error
