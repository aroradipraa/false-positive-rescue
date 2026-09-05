import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

def resolve_and_fetch(url):
    print(f"Fetching: {url}")
    try:
        # Step 1: Follow the lnkd.in redirect
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        r = session.get(url)
        
        final_url = r.url
        # If it's a LinkedIn redirect page, extract the URL from the HTML
        if 'linkedin.com/redir' in final_url or 'linkedin.com' in final_url:
            match = re.search(r'window\.location\.href\s*=\s*"([^"]+)"', r.text)
            if match:
                final_url = match.group(1)
        
        print(f"Resolved to: {final_url}")
        
        # If it's github, fetch the readme
        if 'github.com' in final_url:
            repo_path = final_url.split('github.com/')[-1].strip('/')
            raw_url = f"https://raw.githubusercontent.com/{repo_path}/main/README.md"
            readme_r = session.get(raw_url)
            if readme_r.status_code == 404:
                raw_url = f"https://raw.githubusercontent.com/{repo_path}/master/README.md"
                readme_r = session.get(raw_url)
            
            print("--- README CONTENT START ---")
            print(readme_r.text[:800])
            print("--- README CONTENT END ---")
            
    except Exception as e:
        print(f"Error: {e}")

import re
resolve_and_fetch("https://lnkd.in/gZuB8y-h")
resolve_and_fetch("https://lnkd.in/dA8kFK2T")
