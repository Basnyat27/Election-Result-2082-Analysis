import os
import requests
import pandas as pd
from pathlib import Path
import urllib3

# Hide SSL warnings from website requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_images(df, url_col, name_col, folder_name):
    """
    Downloads images from a DataFrame column and saves them into a local folder.
    """
    # Create the folder if it does not exist
    save_dir = Path(__file__).parent / folder_name
    save_dir.mkdir(parents=True, exist_ok=True)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # Get unique URLs to avoid downloading duplicates
    unique_items = df[[url_col, name_col]].drop_duplicates()
    
    print(f"\n--- Starting download for {folder_name} ---")
    
    for _, row in unique_items.iterrows():
        url = row[url_col]
        item_name = str(row[name_col])
        
        # Skip empty or non-HTTP links
        if pd.isna(url) or not str(url).startswith('http'):
            continue
            
        # Clean item name to create a safe file name (e.g. "Nepali Congress" -> "Nepali_Congress.jpg")
        clean_filename = "".join([c if c.isalnum() else "_" for c in item_name]) + ".jpg"
        file_path = save_dir / clean_filename
        
        # Skip if file was already downloaded
        if file_path.exists():
            print(f"Skipped (Already exists): {clean_filename}")
            continue
            
        try:
            # Download image bytes safely
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            
            # Save raw image data to disk
            with open(file_path, 'wb') as f:
                f.write(response.content)
                
            print(f"Saved: {clean_filename}")
            
        except Exception as e:
            print(f"Failed to download {item_name}: {e}")

# --- RUN THE DOWNLOAD ---
if __name__ == "__main__":
    # Load your CSV file
    df = pd.read_csv("cleaned_data_v2.csv")
    
    # 1. Download Party Symbols (uses party_symbol and party_name/id columns)
    download_images(df, url_col='party_symbol', name_col='party_id', folder_name='assets_1by1/party_symbols')
    
    # 2. Download Candidate Photos (uses candidate_photo and candidate_name/id columns)
    download_images(df, url_col='candidate_photo', name_col='candidate_id', folder_name='assets_1by1/candidate_photos')
    
    print("\nDownload process completed!")