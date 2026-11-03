import sys
import re
from lxml import etree as ET
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import RDFS, OWL

# --- Namespaces & Entities ---
LEMON = Namespace("http://lemon-model.net/lemon#")
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
WN_ONT = Namespace("http://wordnet-rdf.princeton.edu/ontology#")
ISOCAT = Namespace("http://www.isocat.org/datcat/")
DCR = Namespace("http://www.isocat.org/ns/dcr.rdf#")
MIA_LEX = Namespace("http://myaamiadictionary.org/lexicon/")

# ISOcat mappings from build_ontology.py
ISOCAT_LINKS = {
    "noun": 1333,
    "verb": 1424,
    "adjective": 1230,
    "adverb": 1232,
    "gloss": 244,
    "sample": 455,
    "translation": 2970
}

def uncamelcase(label):
    return re.sub("([A-Z])"," \g<0>",label).lstrip().capitalize()

def lift_to_lemon_onto(lift_path):
    g = Graph()
    # Bind prefixes for clean Turtle/RDF output
    g.bind("lemon", LEMON)
    g.bind("ontolex", ONTOLEX)
    g.bind("wn-ont", WN_ONT)
    g.bind("isocat", ISOCAT)
    g.bind("dcr", DCR)
    g.bind("mia", MIA_LEX)

    tree = ET.parse(lift_path)
    root = tree.getroot()

    # Define the Ontology Header
    onto_uri = MIA_LEX["ontology"]
    g.add((onto_uri, RDF.type, OWL.Ontology))
    g.add((onto_uri, OWL.imports, URIRef("http://lemon-model.net/lemon")))

    for entry in root.xpath("//entry"):
        entry_id = entry.get('id')
        entry_uri = MIA_LEX[entry_id]

        # 1. Define Lexical Entry with ISOcat Annotations
        g.add((entry_uri, RDF.type, ONTOLEX.LexicalEntry))
        
        # 2. Canonical Form
        for form in entry.xpath("./lexical-unit/form"):
            lang = form.get('lang')
            text = form.findtext("text")
            form_uri = URIRef(f"{entry_uri}#Form")
            g.add((entry_uri, ONTOLEX.canonicalForm, form_uri))
            g.add((form_uri, RDF.type, ONTOLEX.Form))
            g.add((form_uri, ONTOLEX.writtenRep, Literal(text, lang=lang)))

        # 3. Senses & Grammatical Info (The "Verb Glue")
        for i, sense in enumerate(entry.xpath("./sense")):
            sense_uri = URIRef(f"{entry_uri}#Sense{i}")
            g.add((entry_uri, ONTOLEX.sense, sense_uri))
            
            # POS Mapping to ISOCAT
            gram_info = sense.xpath("./grammatical-info")
            if gram_info:
                pos_val = gram_info[0].get('value').lower()
                if pos_val in ISOCAT_LINKS:
                    dc_id = ISOCAT_LINKS[pos_val]
                    # Link the Myaamia POS to the global ISOcat definition
                    g.add((entry_uri, ONTOLEX.partOfSpeech, ISOCAT.term(f"DC-{dc_id}")))
                    g.add((ISOCAT.term(f"DC-{dc_id}"), RDFS.label, Literal(pos_val, lang="en")))

            # Glosses as dcr:datcat DC-244
            for gloss in sense.xpath("./gloss"):
                gloss_text = gloss.findtext("text")
                g.add((sense_uri, ONTOLEX.definition, Literal(gloss_text, lang=gloss.get('lang'))))
                # Add the specific ontology annotation for 'gloss'
                g.add((sense_uri, DCR.datcat, ISOCAT.term(f"DC-{ISOCAT_LINKS['gloss']}")))

    output_rdf = lift_path.replace('.lift', '.rdf')
    g.serialize(destination=output_rdf, format="pretty-xml")
    print(f"✅ Ontology-ready RDF generated: {output_rdf}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lift_to_lemon_onto(sys.argv[1])
