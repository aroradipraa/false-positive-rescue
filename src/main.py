import csv
import time
from agent import RescueAgent
from mock_apis import TelecomAPI, OpenBankingAPI

def ingest_blocked_transactions(filepath="blocked_transactions.csv"):
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

def print_dashboard(total_analyzed, rescued_count, revenue_saved):
    print("\n" + "="*60)
    print(" [RAZORPAY: FALSE-POSITIVE RESCUE METRICS] ")
    print("="*60)
    print(f"  Transactions Analyzed : {total_analyzed}")
    print(f"  False Positives Caught: {rescued_count}")
    print(f"  Actual Fraud Blocked  : {total_analyzed - rescued_count}")
    print("-" * 60)
    print(f"  [REVENUE RECOVERED]   : Rs. {revenue_saved:,.2f} INR")
    print("="*60 + "\n")

def process_rescue_pipeline():
    print("\n[INITIALIZING FALSE-POSITIVE RESCUE PIPELINE...]")
    transactions = ingest_blocked_transactions()
    
    if not transactions:
        return
        
    agent = RescueAgent()
    
    # We process exactly 4 transactions for the video demo.
    # This guarantees we stay under Google's strict 5 Requests Per Minute free-tier limit.
    demo_batch = transactions[:4]
    
    print(f"[SYSTEM] Batch processing {len(demo_batch)} high-value blocked transactions...\n")
    
    rescued_count = 0
    revenue_saved = 0.0
    
    for txn in demo_batch:
        amt = float(txn['amount_inr'])
        print(f"[*] Analyzing TXN: {txn['txn_id']} | Amount: ₹{amt:,.2f} | IP Risk: {txn['ip_risk_score']}")
        
        telecom_data = TelecomAPI.check_roaming_status(txn['user_id'], int(txn['ip_risk_score']))
        banking_data = OpenBankingAPI.check_account_velocity(txn['user_id'], amt, txn['true_label'])
        
        try:
            decision = agent.evaluate_transaction(txn, telecom_data, banking_data)
            
            if decision == "RESCUE":
                print(f"   [+] [DECISION: RESCUE] AI Verified Legitimate User. Revenue recovered!")
                rescued_count += 1
                revenue_saved += amt
            else:
                print(f"   [-] [DECISION: MAINTAIN BLOCK] AI Confirmed High Fraud Probability.")
        except Exception as e:
            print(f"   [ERROR] AI API Error: {e}")
            
        time.sleep(12) # 12 seconds x 4 requests = 48 seconds (keeps us under 5 RPM limit)
        
    print_dashboard(len(demo_batch), rescued_count, revenue_saved)

if __name__ == "__main__":
    process_rescue_pipeline()
