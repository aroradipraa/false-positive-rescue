import csv
import time
from agent import RescueAgent
from mock_apis import TelecomAPI, OpenBankingAPI

def ingest_blocked_transactions(filepath="blocked_transactions.csv"):
    """Reads the synthetic dataset of blocked transactions."""
    transactions = []
    try:
        with open(filepath, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                transactions.append(row)
    except FileNotFoundError:
        print("[ERROR] Dataset not found.")
        return []
    return transactions

def process_rescue_pipeline():
    """
    Core execution loop. Feeds blocked transactions to the AI Agent.
    """
    print("\n🚀 INITIALIZING FALSE-POSITIVE RESCUE PIPELINE...")
    transactions = ingest_blocked_transactions()
    
    if not transactions:
        return
        
    agent = RescueAgent()
    
    # We sample 10 transactions for the live demo to avoid API rate limits
    demo_batch = transactions[:10]
    
    print(f"[SYSTEM] Batch processing {len(demo_batch)} high-value blocked transactions...\n")
    
    for txn in demo_batch:
        print(f"[*] Analyzing TXN: {txn['txn_id']} | Amount: ₹{txn['amount_inr']} | IP Risk: {txn['ip_risk_score']}")
        
        # 1. Gather invisible secondary data
        telecom_data = TelecomAPI.check_roaming_status(txn['user_id'], int(txn['ip_risk_score']))
        banking_data = OpenBankingAPI.check_account_velocity(txn['user_id'], float(txn['amount_inr']), txn['true_label'])
        
        # 2. Agent Evaluation
        decision = agent.evaluate_transaction(txn, telecom_data, banking_data)
        
        if decision == "RESCUE":
            print(f"   ✅ [DECISION: RESCUE] Legitimate user verified. Revenue recovered!")
        else:
            print(f"   ❌ [DECISION: MAINTAIN BLOCK] High fraud probability confirmed.")
        time.sleep(1) # Prevent rate limiting

if __name__ == "__main__":
    process_rescue_pipeline()
