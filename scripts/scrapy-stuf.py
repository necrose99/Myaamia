import scrapy
import json
import xml.etree.ElementTree as ET
from datetime import datetime

class ScrappieSpider(scrapy.Spider):
    name = 'scrappie'
    
    def __init__(self, url=None, iso=None, *args, **kwargs):
        super(ScrappieSpider, self).__init__(*args, **kwargs)
        # Convert user URL to API endpoint if it's an Atlas-Ling site
        if "atlas-ling.ca" in url or "algonquianlanguages.ca" in url:
            self.start_urls = [url.split("#")[0].rstrip('/') + "/api/v1/entries/"]
        else:
            self.start_urls = [url]
            
        self.iso = iso
        self.entries = []

    def parse(self, response):
        data = json.loads(response.text)
        
        for item in data.get('results', []):
            entry = {
                "id": item.get('id'),
                "native": item.get('headword'),
                "en": item.get('definition') or item.get('gloss'),
                "pos": item.get('part_of_speech', 'unk'),
                "url": response.url
            }
            self.entries.append(entry)

        # "Has More" - Pagination loop
        if data.get('next'):
            yield scrapy.Request(url=data['next'], callback=self.parse)

    def closed(self, reason):
        self.export_to_tmx()

    def export_to_tmx(self):
        output_file = f"{self.iso}_mirror_dump.tmx"
        xml_ns = "http://www.w3.org/XML/1998/namespace"
        
        root = ET.Element("tmx", version="1.4")
        header = ET.SubElement(root, "header", {
            "creationtool": "Scrappie-Mirror",
            "adminlang": "en-US",
            "srclang": "en-US",
            "datatype": "PlainText"
        })
        body = ET.SubElement(root, "body")

        for e in self.entries:
            tu = ET.SubElement(body, "tu", tuid=f"{self.iso}-{e['id']}")
            ET.SubElement(tu, "prop", type="x-pos").text = str(e['pos'])
            
            # English
            tuv_en = ET.SubElement(tu, "tuv")
            tuv_en.set(f"{{{xml_ns}}}lang", "en-US")
            ET.SubElement(tuv_en, "seg").text = e['en']
            
            # Native ISO
            tuv_nat = ET.SubElement(tu, "tuv")
            tuv_nat.set(f"{{{xml_ns}}}lang", self.iso)
            ET.SubElement(tuv_nat, "seg").text = e['native']

        tree = ET.ElementTree(root)
        ET.indent(tree)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"✨ Mirror Complete: {len(self.entries)} entries published to {output_file}")