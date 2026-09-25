import requests, os, sys
from dotenv import load_dotenv
load_dotenv()

base = os.getenv("ANTHROPIC_BASE_URL")
key = os.getenv("ANTHROPIC_API_KEY")

models = ["claude-sonnet-4-6", "claude-opus-4-6", "claude-opus-4-7"]
for model in models:
    try:
        r = requests.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "max_tokens": 100, "messages": [
                {"role": "user", "content": "Answer in Vietnamese: What is the Shopee return policy deadline? Use max 2 sentences."}
            ]},
            timeout=15
        )
        txt = r.json()
        ans = txt.get("choices", [{}])[0].get("message", {}).get("content", "N/A")
        print(f"[{model}]")
        print(ans[:200])
        print()
    except Exception as e:
        print(f"[{model}] ERROR: {e}")
