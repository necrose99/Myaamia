from lxml import etree
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

# Import your generated models
from linguistic_models.lift import Lift
# Note: Ensure you have a Lemon class generated from a lemon.xsd as well
# from linguistic_models.lemon import Lemon 

class LinguisticTransformer:
    def __init__(self, lemon2lift_path="Lemon2LIFT.xslt", lift2lemon_path="LIFT2lemon.xslt"):
        self.parser = XmlParser()
        self.serializer = XmlSerializer(config=SerializerConfig(pretty_print=True))
        
        # Load XSLT stylesheets
        self.lemon2lift_xslt = etree.XSLT(etree.parse(lemon2lift_path))
        self.lift2lemon_xslt = etree.XSLT(etree.parse(lift2lemon_path))

    def to_lift_obj(self, lemon_xml_path):
        """Transforms Lemon XML file into a LIFT Python Object"""
        xml_doc = etree.parse(lemon_xml_path)
        transformed_xml = self.lemon2lift_xslt(xml_doc)
        # Parse the resulting XML string into the Lift dataclass
        return self.parser.from_string(str(transformed_xml), Lift)

    def to_lemon_xml(self, lift_obj):
        """Transforms a LIFT Python Object back into Lemon XML string"""
        # 1. Convert Lift object back to XML string
        lift_xml_str = self.serializer.render(lift_obj)
        lift_xml_doc = etree.fromstring(lift_xml_str.encode('utf-8'))
        
        # 2. Run the reverse XSLT
        lemon_xml = self.lift2lemon_xslt(lift_xml_doc)
        return str(lemon_xml)

# --- Example Usage for your Flask Backend ---
# transformer = LinguisticTransformer()

# 1. Convert Lemon -> LIFT Object (to save in SQLite)
# lift_data = transformer.to_lift_obj("input_lemon.xml")
# print(f"First Entry: {lift_data.entries[0].lexical_unit}")

# 2. Convert LIFT Object -> Lemon XML (to export/download)
# lemon_output = transformer.to_lemon_xml(lift_data)
