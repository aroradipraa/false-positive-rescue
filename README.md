# False-Positive Rescue Engine

An autonomous risk-evaluation pipeline designed to recover lost merchant revenue by identifying and rescuing false-positive fraud blocks.

## Architecture

Primary machine learning models often prioritize strict safety, resulting in a high rate of false positives (legitimate customers being blocked). This engine sits downstream of the primary fraud model and utilizes a "Cascade Funnel" architecture to safely override blocks without increasing fraud leakage.

### 1. Deterministic Filtering
To optimize API costs and throughput, 95% of blocked transactions are evaluated locally using strict deterministic rules. Obvious fraud is maintained, while highly ambiguous edge cases are escalated.

### 2. Multi-Modal Triangulation
Escalated transactions are passed to a Gemini 3.6 reasoning agent. Rather than relying solely on the transaction metadata, the agent triangulates identity using two external data sources:
- **Telecom API:** Verifies if the device's current roaming geolocation matches the IP address used at checkout.
- **Open Banking API:** Analyzes historical account velocity to confirm if the user has a legitimate financial footprint.

### 3. Rule-Based Authorization
"Models interpret; rules authorize." The LLM evaluates the context, but the final decision is mathematically gated. If the telecom location mismatches or the banking velocity is suspicious, the transaction remains blocked.

## Benchmark Metrics

Evaluated against a synthetic holdout batch of 1,000 blocked transactions:
- **Triangulation Precision:** 99.8%
- **Fraud Leakage Rate:** 0.0%
- **AI Escalations:** ~5% of total volume

## Local Execution

Requires Python 3.9+.

```bash
pip install streamlit pandas google-genai python-dotenv
```

Configure your environment variables:
```bash
# .env
GEMINI_API_KEY="your_api_key_here"
```

Execute the command center UI:
```bash
python -m streamlit run src/app.py
```
