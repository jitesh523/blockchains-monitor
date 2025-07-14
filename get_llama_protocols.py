"""
get_llama_protocols.py
Fetch and print protocol slugs from DeFi Llama for diagnostic use.
"""
import requests

def main():
    url = "https://api.llama.fi/protocols"
    resp = requests.get(url)
    resp.raise_for_status()
    protocols = resp.json()
    for p in protocols:
        print(f"{p['name']} : {p['slug']}")

if __name__ == "__main__":
    main()

