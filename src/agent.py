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

    def evaluate_transaction(self, txn_data: dict, telecom_data: dict, banking_data: dict) -> dict:
        prompt = f"""
        You are an AI Risk Manager for a Payment Gateway.
        A transaction was BLOCKED by the primary fraud ML model. You must decide whether to RESCUE (unblock) it or keep it BLOCKED.
        
        Original Transaction Data:
        {json.dumps(txn_data, indent=2)}
        
        Secondary Triangulation Data (Gathered invisibly):
        Telecom Geolocation: {json.dumps(telecom_data, indent=2)}
        Open Banking Velocity: {json.dumps(banking_data, indent=2)}
        
        Rules:
        1. If Telecom location matches AND Banking shows good historical velocity (older account, high monthly velocity), this user is legitimate (False Positive). Decision: RESCUE.
        2. If either secondary check fails, looks suspicious, or shows a brand new burner account, this is actual fraud. Decision: MAINTAIN_BLOCK.
        
        You must evaluate the evidence and provide a confidence score between 0.0 and 100.0 representing how certain you are in your decision based on the API evidence.
        
        Respond STRICTLY in valid JSON format exactly like this:
        {{"decision": "RESCUE", "confidence_score": 98.5}}
        """
        
        # Using the required gemini-3.6-flash model for new accounts
        response = self.client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt
        )
        
        try:
            # Clean up potential markdown formatting from LLM response
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            result = json.loads(raw_text)
            
            # Ensure safe fallback values if LLM formats weirdly
            return {
                "decision": result.get("decision", "MAINTAIN_BLOCK").upper(),
                "confidence": float(result.get("confidence_score", 90.0))
            }
        except Exception as e:
            # Safe fail-open back to block if the LLM hallucinates non-JSON
            return {"decision": "MAINTAIN_BLOCK", "confidence": 0.0}
