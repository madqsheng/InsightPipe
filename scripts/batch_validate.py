import requests
import json
import re
import os
import time

# --- CONFIGURATION (The "Golden" Session) ---
BASE_URL = "https://gemini.google.com/_/BardChatUi/data/batchexecute"

# Minimal Params (Proved to work in Test 2)
QUERY_PARAMS_TEMPLATE = {
    "rpcids": "ujx1Bf",
    "hl": "zh-CN",
    "rt": "c"
}

HEADERS = {
    "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    # The valid cookies
    "cookie": "_gcl_au=1.1.1678809549.1769051420; NID=528=XZyVJ9pubNj3FwezA4SUDWyr3CJLvv829fBf4Y_vsT30EKqIwlcX-yHsPI8Wzml-HwQfpMmoY5cS3EfMukb3pxoI_Ff2r7S_DP6owRZ_LkP7Y0AsCA2RGizxQ3tcCav7L63nmmiyq44LSZx-pvNmopVxXa4b0tUNIcr6KsaJqgFIbOOiCFDcBodklSEe8Zwl20x4KkciT_oWI78; _ga_WC57KJ50ZZ=GS2.1.s1769051419$o1$g0$t1769051419$j60$l0$h0; _ga=GA1.1.946165692.1769051420; COMPASS=gemini-pd=CjwACWuJV93jFYb_b6k1ZbZc5AVi75OXfwVJx6huPFdJgLZgT-iphNSBtyIyTho-2Gurv4U86El7hPmdVFUQnM3LywYaTQAJa4lXIkN3sOK5jSzDLo2KoxQKl9Bgki7C7N4fLHso4yScK57z7OtHDPXawsZ63IvG9HHHWfhbYkNI8LQLixZ0PclguOc_5RUrTwfQIAEwAQ; _ga_BF8Q35BMLM=GS2.1.s1769051420$o1$g0$t1769051420$j60$l0$h0"
}

DATA_DIR = "gemini_data_samples"

def extract_id(url):
    match = re.search(r'share/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None

def process_link(url):
    share_id = extract_id(url)
    if not share_id:
        print(f"❌ Invalid Link: {url}")
        return

    print(f"\n🔄 Fetching Raw Data for ID: {share_id}...")
    
    params = QUERY_PARAMS_TEMPLATE.copy()
    params["source-path"] = f"/share/{share_id}"
    
    # Payload Construction
    inner_req = f'[null,"{share_id}",[4]]'
    payload = {
        "f.req": f'[[["ujx1Bf","{inner_req.replace('"', '\\"')}",null,"generic"]]]',
        "at": ""
    }
    
    try:
        resp = requests.post(BASE_URL, params=params, data=payload, headers=HEADERS, timeout=15)
        
        # Save RAW response regardless of status code
        filename = f"{DATA_DIR}/{share_id}_raw.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(resp.text)
            
        print(f"💾 Saved raw response to {filename} (Status: {resp.status_code}, Size: {len(resp.text)} chars)")

    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    with open(f"{DATA_DIR}/links.txt", "r") as f:
        links = [l.strip() for l in f.readlines() if l.strip()]
    
    print(f"🧪 Starting Batch Download on {len(links)} links...")
    print("---------------------------------------------------")
    
    for link in links:
        process_link(link)
        time.sleep(1) # Be polite

if __name__ == "__main__":
    main()
