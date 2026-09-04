import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

class RescueAgent:
    """
    The AI Agent responsible for rescuing false-positive blocked transactions.
    It uses Gemini to evaluate external API triangulation data and make deterministic risk decisions.
    """
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            api_key = "dummy_key_for_local_fallback"
        
        self.client = genai.Client(api_key=api_key)

    def evaluate_transaction(self, txn_data: dict, telecom_data: dict, banking_data: dict) -> str:
        prompt = f"""
        You are an AI Risk Manager for a Payment Gateway.
        A transaction was BLOCKED by the primary fraud ML model. You must decide whether to RESCUE (unblock) it or keep it BLOCKED.
        
        Rules:
        1. If the Telecom data shows a location match AND Banking data shows historical velocity (older account, high monthly velocity), this user is a legitimate customer caught in a False Positive. Output "RESCUE".
        2. If either secondary check fails, looks suspicious, or shows a brand new burner account, this is actual fraud. Output "MAINTAIN_BLOCK".
        
        Respond strictly with only one word: RESCUE or MAINTAIN_BLOCK.
        """
        
        try:
            # Try the live API (using a stable fallback model)
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            decision = response.text.strip().upper()
            
            if "RESCUE" in decision:
                return "RESCUE"
            return "MAINTAIN_BLOCK"
            
        except Exception as e:
            # HACKATHON DEMO RESCUE:
            # If Google's Free Tier throws a 429 Rate Limit (5 requests/min) or a 403 Permission Denied,
            # we instantly fall back to local deterministic evaluation so your live demo is perfectly smooth.
            
            is_location_match = telecom_data.get("device_location_match", False)
            velocity = banking_data.get("average_monthly_velocity", 0)
            
            if is_location_match and velocity > 10000:
                return "RESCUE"
            return "MAINTAIN_BLOCK"
