# helpers/wals_scraper.py
import requests
from bs4 import BeautifulSoup
import sqlite3

def harvest_wals_features(wals_code="ill"):
    """
    Queries WALS Online to resolve modern typological parameters 
    and checks morphological alignments before map execution.
    """
    url = f"https://wals.info_{wals_code}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200: return {}
        
        soup = BeautifulSoup(r.text, 'html.parser')
        features = {}
        
        # Scrape and locate specific structural feature rows
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 3:
                feature_name = cells[2].text.strip()
                feature_value = cells[1].text.strip()
                if "Hand and Arm" in feature_name:
                    features["129A"] = feature_value
                elif "Finger and Hand" in feature_name:
                    features["130A"] = feature_value
        return features
    except Exception as e:
        print(f"Failed parsing typological index: {e}")
        return {}
