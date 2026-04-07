import lxml.etree as ET
from bs4 import BeautifulSoup

def guided_crawl(tmx_path, html_path):
    # Load the TMX "Map"
    tmx_tree = ET.parse(tmx_path)
    tmx_ids = tmx_tree.xpath("//prop[@type='x-ilda-id']/text()")
    
    # Load the Raw HTML "Mine"
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')

    cleaned_data = []

    for ilda_id in tmx_ids:
        # Search the HTML for a tag containing this specific ID
        # Many ILDA exports embed the ID in a data-attribute or link
        target_link = soup.find('a', href=re.compile(f"entries/{ilda_id}"))
        
        if target_link:
            # We found the "Linguistic Anchor" in the mess!
            # Now we extract the sibling data (Usage Examples, etc.)
            parent_row = target_link.find_parent('tr')
            examples = parent_row.find_all('div', class_='usage-example')
            
            cleaned_data.append({
                "id": ilda_id,
                "examples": [ex.get_text(strip=True) for ex in examples]
            })
            
    return cleaned_data
