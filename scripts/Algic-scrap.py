import scrapy
import re

class AlgicCrawlSpider(scrapy.Spider):
    name = 'algic_crawl'
    
    def start_requests(self):
        # We can now iterate through your expanded algic_array 
        # or a curated subset of URLs
        for lang in self.language_array:
            yield scrapy.Request(
                url=lang['url'], 
                callback=self.get_handler(lang['url']), 
                meta={'lang_meta': lang}
            )

    def get_handler(self, url):
        """Routes the URL to the specific parsing strategy."""
        if 'miamioh.edu' in url: return self.parse_ilda
        if 'omniglot.com' in url: return self.parse_omniglot
        if 'native-languages.org' in url: return self.parse_native_langs
        return self.parse_generic

    def parse_ilda(self, response):
        """High-fidelity extraction for Myaamia ILDA (Weight 1.0)"""
        for entry in response.css('.dictionary-entry'):
            yield {
                'en': entry.css('.english-gloss::text').get(),
                'mia': entry.css('.myaamia-term::text').get(),
                'audio_url': response.urljoin(entry.css('source::attr(src)').get()),
                'iso': 'mia',
                'weight': 1.0,
                'source': 'ILDA'
            }

    def parse_omniglot(self, response):
        """IPA and Orthography extraction for Cousins."""
        meta = response.meta['lang_meta']
        # Omniglot uses a specific table structure for 'Useful Phrases'
        for row in response.xpath('//table[contains(@class, "alphabet")]//tr'):
            cols = row.xpath('td//text()').getall()
            if len(cols) >= 2:
                yield {
                    'en': cols[0].strip(),
                    'target': cols[1].strip(),
                    'iso': meta['iso'],
                    'weight': meta['weight'],
                    'type': 'ipa_phrase'
                }

    def parse_native_langs(self, response):
        """Pattern matching for unstructured vocabulary lists."""
        meta = response.meta['lang_meta']
        # Targeted regex to find "English: Native" patterns in the mess of HTML
        text_content = response.xpath('//div[@id="content"]//text()').getall()
        for line in text_content:
            match = re.search(r'([A-Za-z\s]+):\s*([^\n]+)', line)
            if match:
                yield {
                    'en': match.group(1).strip(),
                    'target': match.group(2).strip(),
                    'iso': meta['iso'],
                    'weight': meta['weight']
                }
# Logic to handle Mexican Kickapoo shards
if lang_meta['iso'] == 'kic' and 'mexico' in response.url:
    yield {
        'es': spanish_gloss,
        'kic': kickapoo_term,
        'notes': "Sourced from Coahuila/Muzquiz records"
    }
# Expanded metadata to handle the gloss source
language_array = [
    {'iso': 'mia', 'url': '...', 'gloss_lang': 'fr', 'weight': 1.0}, # Le Boulanger (Archaic)
    {'iso': 'kic', 'url': '...', 'gloss_lang': 'es', 'weight': 0.8}, # Kickapoo (Mexican/Muzquiz)
    {'iso': 'sac', 'url': '...', 'gloss_lang': 'en', 'weight': 0.9}  # Sauk Workbook
]
from deep_translator import GoogleTranslator

def align_bridge_languages(db_cursor):
    """
    Translates French (Jesuit) or Spanish (Kickapoo) glosses 
    into English to create a unified Master English ID.
    """
    # 1. Grab rows where we have a French gloss but no English yet
    db_cursor.execute("SELECT id, fr_text, es_text FROM TranslationUnits WHERE en_text IS NULL")
    rows = db_cursor.fetchall()

    for row_id, fr, es in rows:
        if fr:
            # Bridge French to English
            en_bridge = GoogleTranslator(source='fr', target='en').translate(fr)
        elif es:
            # Bridge Spanish to English
            en_bridge = GoogleTranslator(source='es', target='en').translate(es)
        
        # 2. Update the row so the 'en_text' becomes the primary key for the RAG
        db_cursor.execute("UPDATE TranslationUnits SET en_text = ? WHERE id = ?", (en_bridge.lower(), row_id))
