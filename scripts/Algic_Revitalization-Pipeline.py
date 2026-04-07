import requests
import zipfile
from io import BytesIO
import xml.etree.ElementTree as ET
import pandas as pd

# Download the TMX file
url = "https://github.com/necrose99/Myaamia/raw/master/target/Algic.tmx"
response = requests.get(url)
tms_content = response.content

# Parse TMX
def parse_tmx(tmx_content):
    """Parse TMX XML into a DataFrame."""
    root = ET.fromstring(tmx_content)
    
    entries = []
    for tu in root.findall('.//tu'):
        tuv = tu.find('.//tuv')
        if tuv is not None:
            lang = tuv.get('{http://www.w3.org/XML/1998/namespace}lang')
            seg = tuv.find('seg')
            if seg is not None and seg.text:
                entries.append({
                    'language': lang,
                    'text': seg.text.strip(),
                    'source': lang.split('-')[0]  # Get primary language code
                })
    
    return pd.DataFrame(entries)

# Parse the TMX
df_tmx = parse_tmx(tms_content)
print(f"✅ Loaded {len(df_tmx)} TMX entries")
print(f"🌐 Languages found: {df_tmx['language'].unique()}")

# Show preview
print("\n🔍 TMX Preview:")
print(df_tmx.head(10))
