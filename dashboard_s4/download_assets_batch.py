import os
import re
import pandas as pd
import requests
import urllib3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Suppress SSL certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- ⚙️ SETUP YOUR COLUMNS HERE ---
# Write the EXACT column names as they appear in your CSV
PARTY_URL_COL = 'party_symbol'
PARTY_NAME_COL = 'party_id'           # <--- Change this to match your CSV (e.g., 'party_name', 'party')

CANDIDATE_URL_COL = 'candidate_photo'
CANDIDATE_NAME_COL = 'candidate_id' # <--- Change this to match your CSV
# -----------------------------------

def sanitize_filename(name):
    """Removes spaces and invalid characters from names to make safe file names."""
    clean = re.sub(r'[^\w\s-]', '', str(name)).strip()
    return re.sub(r'[-\s]+', '_', clean)

def download_single_image(task):
    """Downloads a single image (used by the ThreadPoolExecutor)"""
    url, file_path = task
    
    # Skip if no URL or file already exists
    if pd.isna(url) or not str(url).startswith('http') or file_path.exists():
        return False
        
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        
        if resp.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(resp.content)
            return True
    except Exception:
        pass
        
    return False

def batch_download(df, url_col, name_col, folder_name):
    """Prepares the download tasks and runs them concurrently."""
    # Safety Check: Ensure the columns actually exist in the CSV!
    if url_col not in df.columns or name_col not in df.columns:
        print(f"❌ ERROR: Missing columns for {folder_name}!")
        print(f"   Could not find '{url_col}' or '{name_col}'.")
        print(f"   Available columns in your CSV are: {df.columns.tolist()}\n")
        return

    # Create directories
    save_dir = Path(__file__).parent / folder_name
    save_dir.mkdir(parents=True, exist_ok=True)

    # Filter out empty rows and remove duplicates
    unique_items = df[[url_col, name_col]].dropna().drop_duplicates()
    
    # Create a list of tasks: (URL, Destination_Path)
    tasks = []
    for _, row in unique_items.iterrows():
        filename = sanitize_filename(row[name_col]) + ".jpg"
        file_path = save_dir / filename
        tasks.append((row[url_col], file_path))

    print(f"🔄 Downloading {len(tasks)} items to '{folder_name}'...")
    
    # Run 15 downloads at the exact same time!
    with ThreadPoolExecutor(max_workers=15) as executor:
        results = list(executor.map(download_single_image, tasks))
        
    success_count = sum(1 for r in results if r)
    print(f"✅ Finished! Successfully downloaded {success_count} new images to '{folder_name}'.\n")

if __name__ == "__main__":
    # Ensure correct path to your CSV
    csv_path = Path(__file__).parent / "cleaned_data_v2.csv"
    
    if not csv_path.exists():
        print(f"❌ Cannot find CSV file at: {csv_path}")
        print("Please ensure this script is in the 'dashboard_s4' folder.")
    else:
        df = pd.read_csv(csv_path)
        
        # Run downloads
        batch_download(df, PARTY_URL_COL, PARTY_NAME_COL, 'assets_best/party_symbols')
        batch_download(df, CANDIDATE_URL_COL, CANDIDATE_NAME_COL, 'assets_best/candidate_photos')