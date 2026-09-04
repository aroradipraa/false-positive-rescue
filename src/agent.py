import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

class RescueAgent:
    """
    The AI Agent responsible for rescuing false-positive blocked transactions.
    """
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key is missing. Add it to your .env file.")
        
        self.client = genai.Client(api_key=api_key)

    def evaluate_transaction(self, txn_data: dict, telecom_data: dict, banking_data: dict) -> str:
        prompt = f"""
        You are an AI Risk Manager for a Payment Gateway.
        A transaction was BLOCKED by the primary fraud ML model. You must decide whether to RESCUE (unblock) it or keep it BLOCKED.
        
        Original Transaction Data:
        {json.dumps(txn_data, indent=2)}
        
        Secondary Triangulation Data (Gathered invisibly):
        Telecom Geolocation: {json.dumps(telecom_data, indent=2)}
        Open Banking Velocity: {json.dumps(banking_data, indent=2)}
        
        Rules:
        1. If the Telecom data shows a location match AND Banking data shows historical velocity (older account, high monthly velocity), this user is a legitimate customer caught in a False Positive. Output "RESCUE".
        2. If either secondary check fails, looks suspicious, or shows a brand new burner account, this is actual fraud. Output "MAINTAIN_BLOCK".
        
        Respond strictly with only one word: RESCUE or MAINTAIN_BLOCK.
        """
        
        # Using the required gemini-3.6-flash model for new accounts
        response = self.client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt
        )
        decision = response.text.strip().upper()
        
        if "RESCUE" in decision:
            return "RESCUE"
        return "MAINTAIN_BLOCK"
