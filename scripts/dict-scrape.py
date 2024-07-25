import requests
from bs4 import BeautifulSoup
import json

def scrape_entry(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    entry = {}
    
    # Get the main word and its type
    title = soup.find('h1', class_='entry-title').text.strip()
    entry['word'], entry['type'] = title.split('(')
    entry['type'] = entry['type'].strip(')')
    
    # Get the definition
    definition = soup.find('div', class_='definition')
    if definition:
        entry['definition'] = definition.text.strip()
    
    # Get basic forms
    basic_forms = soup.find('table', class_='basic-forms')
    if basic_forms:
        entry['basic_forms'] = []
        rows = basic_forms.find_all('tr')
        for row in rows[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 2:
                entry['basic_forms'].append({
                    'myaamia': cols[0].text.strip(),
                    'english': cols[1].text.strip()
                })
    
    # Get example sentences
    example_sentences = soup.find('table', class_='example-sentences')
    if example_sentences:
        entry['example_sentences'] = []
        rows = example_sentences.find_all('tr')
        for row in rows[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 2:
                entry['example_sentences'].append({
                    'myaamia': cols[0].text.strip(),
                    'english': cols[1].text.strip()
                })
    
    return entry

def scrape_dictionary(base_url, num_entries=100):
    entries = []
    for i in range(1, num_entries + 1):
        url = f"{base_url}{i}"
        try:
            entry = scrape_entry(url)
            entries.append(entry)
            print(f"Scraped entry {i}: {entry['word']}")
        except Exception as e:
            print(f"Error scraping entry {i}: {str(e)}")
    
    return entries

# Main execution
base_url = "https://mc.miamioh.edu/ilda-myaamia/dictionary/entries/"
entries = scrape_dictionary(base_url, num_entries=100)

# Save to JSON
with open('myaamia_dictionary.json', 'w', encoding='utf-8') as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print("Dictionary entries saved to myaamia_dictionary.json")