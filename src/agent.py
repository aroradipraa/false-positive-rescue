import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class RescueAgent:
    """
    The AI Agent responsible for rescuing false-positive blocked transactions.
    It uses Gemini to evaluate external API triangulation data and make deterministic risk decisions.
    """
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "PASTE_YOUR_GEMINI_KEY_HERE":
            raise ValueError("Gemini API key is missing. Add it to your .env file.")
        
        genai.configure(api_key=api_key)
        # Using flash for high-throughput, low-latency evaluation
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def evaluate_transaction(self, txn_data: dict, telecom_data: dict, banking_data: dict) -> str:
        """
        Asks the LLM to act as a Risk Manager. It looks at the original blocked transaction
        and the new triangulated data to decide if it should be RESCUED.
        """
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
        
        try:
            response = self.model.generate_content(prompt)
            decision = response.text.strip().upper()
            
            if "RESCUE" in decision:
                return "RESCUE"
            return "MAINTAIN_BLOCK"
            
        except Exception as e:
            # Strict Fail-Closed Architecture: If the LLM times out or errors, do NOT rescue.
            print(f"[ERROR] LLM Evaluation failed: {e}")
            return "MAINTAIN_BLOCK"
