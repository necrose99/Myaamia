import scrapy
import lxml.etree as ET
from datetime import datetime

class MahkihkiwaSpider(scrapy.Spider):
    name = "mahkihkiwa"
    start_urls = ["https://mc.miamioh.edu/mahkihkiwa/species?order-by=species_name&entry_type="]

    def parse(self, response):
        # Follow links to individual species detail pages
        species_links = response.css('table tr td a::attr(href)').getall()
        for link in species_links:
            yield response.follow(link, self.parse_species)

        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_species(self, response):
        # Precision extraction for the botanical 'Soil' layer
        mia = response.css('.myaamia-term::text').get(default="").strip()
        en = response.css('.english-term::text').get(default="").strip()
        
        # Line 28 Patch: Extract Latin accurately even if inside <i> tags
        latin = response.css('.scientific-name ::text').getall()
        latin = " ".join(latin).strip()
        
        notes = " ".join(response.css('.notes-content ::text').getall()).strip()
        
        # Extract French from Jesuit shards if present
        fr = ""
        if "French:" in notes:
            fr = notes.split("French:")[1].split(".")[0].strip()

        yield {
            'mia': mia,
            'en': en,
            'latin': latin,
            'fr': fr,
            'notes': notes
        }

def generate_tmx(data_list, output_file):
    root = ET.Element("tmx", version="1.4")
    header = ET.SubElement(root, "header", {
        "segtype": "phrase", "adminlang": "en-US", "srclang": "en-US",
        "datatype": "PlainText", "creationdate": datetime.now().strftime("%Y%m%dT%H%M%SZ")
    })
    body = ET.SubElement(root, "body")

    for item in data_list:
        if not item['mia']: continue
        
        tu = ET.SubElement(body, "tu")
        
        # Line 62 Patch: Move Latin to a TMX Property for SQL mapping
        prop_latin = ET.SubElement(tu, "prop", type="scientific_name")
        prop_latin.text = item['latin']
        
        # Keep notes for the 16-hour Ollama grind context
        note_el = ET.SubElement(tu, "note")
        note_el.text = item['notes']

        # Segmenting: English, Myaamia, French
        for lang_code, text in [('en', item['en']), ('mia', item['mia']), ('fr', item['fr'])]:
            if text:
                tuv = ET.SubElement(tu, "tuv")
                tuv.set("{http://www.w3.org/XML/1998/namespace}lang", lang_code)
                ET.SubElement(tuv, "seg").text = text

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True, pretty_print=True)
