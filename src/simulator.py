import csv
import random
import uuid

def generate_dataset(filename="blocked_transactions.csv", num_rows=1000):
    """
    Generates a synthetic dataset of transactions that were BLOCKED by a standard fraud engine.
    Injects a specific distribution of actual fraud vs. 'False Positives' (legitimate customers).
    """
    print(f"[SYSTEM] Generating {num_rows} synthetic blocked transactions...")
    
    headers = [
        "txn_id", "user_id", "amount_inr", "ip_risk_score", 
        "distance_from_home_km", "is_vpn", "status", "true_label"
    ]
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
        false_positives = 0
        actual_fraud = 0
        
        for _ in range(num_rows):
            txn_id = f"txn_{uuid.uuid4().hex[:8]}"
            user_id = f"user_{random.randint(1000, 9999)}"
            amount = round(random.uniform(500, 50000), 2)
            
            # The fraud engine blocked this. Why?
            # 70% of the time, it's actual fraud (High IP risk, High distance, VPN)
            # 30% of the time, it's a FALSE POSITIVE (Legit user on a work VPN or traveling)
            
            is_false_positive = random.random() < 0.3
            
            if is_false_positive:
                ip_risk = random.randint(60, 85) # High enough to trigger a block, but not definitely fraud
                distance = random.randint(50, 500) # Traveling
                is_vpn = random.choice([True, False])
                true_label = "LEGITIMATE"
                false_positives += 1
            else:
                ip_risk = random.randint(85, 99) # Blatant fraud
                distance = random.randint(1000, 10000) # International fraud ring
                is_vpn = True
                true_label = "FRAUD"
                actual_fraud += 1
                
            writer.writerow([
                txn_id, user_id, amount, ip_risk, 
                distance, is_vpn, "BLOCKED", true_label
            ])
            
    print("[SUCCESS] Dataset generated successfully.")
    print(f"Stats: {actual_fraud} Actual Fraud | {false_positives} False Positives (Lost Revenue)")
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    generate_dataset(num_rows=5000)
