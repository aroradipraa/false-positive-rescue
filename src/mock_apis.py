import random

class TelecomAPI:
    """
    Simulates a 3rd-party Telecom API (like Truecaller or Twilio).
    Used to check if a user's mobile device is actively roaming in a specific ZIP code,
    which helps prove they are a legitimate traveler, not a fraudster using a VPN.
    """
    @staticmethod
    def check_roaming_status(user_id: str, current_ip_risk: int) -> dict:
        is_roaming_match = current_ip_risk < 90
        return {
            "api_provider": "Telecom-Verify-API",
            "device_location_match": is_roaming_match,
            "confidence_score": random.uniform(0.85, 0.99) if is_roaming_match else random.uniform(0.1, 0.4),
            "latency_ms": random.randint(120, 300)
        }

class OpenBankingAPI:
    """
    Simulates an Account Aggregator / Open Banking API.
    Used to check if the user's bank account has legitimate, historical transaction velocity,
    proving it's a real person's account and not a freshly created burner account for fraud.
    """
    @staticmethod
    def check_account_velocity(user_id: str, amount_inr: float, true_label: str) -> dict:
        # Legit users have high history. Fraudsters often use new burner accounts.
        is_legit = (true_label == "LEGITIMATE")
        
        return {
            "api_provider": "Account-Aggregator-Network",
            "account_age_days": random.randint(300, 2000) if is_legit else random.randint(1, 14),
            "average_monthly_velocity": random.uniform(20000, 150000) if is_legit else random.uniform(0, 5000),
            "sufficient_funds_probability": random.uniform(0.9, 1.0) if is_legit else random.uniform(0.2, 0.6)
        }
