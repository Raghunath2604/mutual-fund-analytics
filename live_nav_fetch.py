import os
import requests
import pandas as pd

TARGET_SCHEMES = {
    "HDFC_Top_100_Direct": 125497,
    "SBI_Bluechip": 119551,
    "ICICI_Bluechip": 120503,
    "Nippon_Large_Cap": 118632,
    "Axis_Bluechip": 119092,
    "Kotak_Bluechip": 120841
}

def fetch_and_save_nav():
    print("Starting live NAV fetch...")
    
    for name, code in TARGET_SCHEMES.items():
        url = f"https://api.mfapi.in/mf/{code}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Parse the JSON response into meta information and actual NAV data
            nav_data = data.get("data", [])
            
            if nav_data:
                # Convert to a Pandas DataFrame
                df = pd.DataFrame(nav_data)
                
                # Save the raw CSV to our designated folder
                file_path = f"data/raw/{name}_{code}.csv"
                df.to_csv(file_path, index=False)
                print(f"✅ Saved {name} to {file_path}")
            else:
                print(f"⚠️ No data found for {name}")
        else:
            print(f"❌ Failed to fetch {name}. HTTP Status: {response.status_code}")

if __name__ == "__main__":
    fetch_and_save_nav()