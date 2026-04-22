import scrapy
import json
from pipelines import AlgicMediaPipeline # Import locally to verify

class AlgicMasterSpider(scrapy.Spider):
    name = 'algic_master'
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'pipelines.AlgicMediaPipeline': 1, # Points to pipelines.py
        },
        'FILES_STORE': r'C:\Users\black\GitHub\Myaamia\corpus_media',
        'FILES_EXPIRES': 90,
        'RETRY_TIMES': 5,
        'DOWNLOAD_DELAY': 0.5
    }

    ATLAS_TARGETS = {
        "crk": "plainscree.algonquianlanguages.ca",
        "atj": "atikamekw.atlas-ling.ca",
        "csw": "dictionary.swampycree.atlas-ling.ca",
        "nsk": "naskapi.atlas-ling.ca",
        "moe": "dictionary.innu-aimun.ca",
        "bft": "dictionary.blackfoot.atlas-ling.ca",
        "crj": "dictionary.eastcree.org",
        "ciw": "nishnaabemwin.atlas-ling.ca",
        "alg-proto": "protoalgonquian.atlas-ling.ca"
    }

    def start_requests(self):
        for iso, domain in self.ATLAS_TARGETS.items():
            url = f"https://{domain}/api/v1/entries/?limit=100"
            yield scrapy.Request(url, callback=self.parse_api, meta={'iso': iso})
        
        yield scrapy.Request('https://mc.miamioh.edu/ilda-myaamia/dictionary/entries', callback=self.parse_ilda_list)

    def parse_api(self, response):
        iso = response.meta['iso']
        data = json.loads(response.text)
        for item in data.get('results', []):
            yield {
                'iso': iso,
                'id': item.get('id'),
                'native': item.get('headword'),
                'en': item.get('definition') or item.get('gloss'),
                'file_urls': [item['audio_url']] if item.get('audio_url') else []
            }
        if data.get('next'):
            yield response.follow(data['next'], self.parse_api, meta={'iso': iso})

    def parse_ilda_list(self, response):
        links = response.css('a[href*="/entries/"]::attr(href)').getall()
        for link in links:
            yield response.follow(link, self.parse_ilda_entry)

    def parse_ilda_entry(self, response):
        media = response.css('source::attr(src)').getall()
        yield {
            'iso': 'mia',
            'id': response.url.split('/')[-1],
            'native': response.css('.headword::text').get(),
            'en': response.css('.definition::text').get(),
            'file_urls': [response.urljoin(m) for m in media]
        }