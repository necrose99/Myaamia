import sys
from lxml import etree as ET
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import RDFS, OWL

# Namespaces based on your XSLT entities
LEMON = Namespace("http://lemon-model.net/lemon#")
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
WN_ONT = Namespace("http://wordnet-rdf.princeton.edu/ontology#")
MIA_LEX = Namespace("http://myaamiadictionary.org/lexicon/")

def lift_to_lemon(lift_path):
    g = Graph()
    g.bind("lemon", LEMON)
    g.bind("ontolex", ONTOLEX)
    g.bind("wn-ont", WN_ONT)
    g.bind("mia", MIA_LEX)

    tree = ET.parse(lift_path)
    root = tree.getroot()

    for entry in root.xpath("//entry"):
        entry_id = entry.get('id')
        entry_uri = MIA_LEX[entry_id]

        # 1. Define Lexical Entry
        g.add((entry_uri, RDF.type, ONTOLEX.LexicalEntry))

        # 2. Map Canonical Form (The Headword)
        for form in entry.xpath("./lexical-unit/form"):
            lang = form.get('lang')
            text = form.findtext("text")
            form_uri = URIRef(f"{entry_uri}#canonicalForm")
            g.add((entry_uri, ONTOLEX.canonicalForm, form_uri))
            g.add((form_uri, RDF.type, ONTOLEX.Form))
            g.add((form_uri, ONTOLEX.writtenRep, Literal(text, lang=lang)))

        # 3. Map Senses and WordNet References
        for i, sense in enumerate(entry.xpath("./sense")):
            sense_id = sense.get('id') or f"{entry_id}-sense-{i}"
            sense_uri = URIRef(f"{entry_uri}#{sense_id}")
            
            g.add((entry_uri, ONTOLEX.sense, sense_uri))
            g.add((sense_uri, RDF.type, ONTOLEX.LexicalSense))

            # Map Gloss to Lexical Definition
            for gloss in sense.xpath("./gloss"):
                g.add((sense_uri, RDFS.comment, Literal(gloss.findtext("text"), lang=gloss.get('lang'))))

            # Logic for "Verb Glue" / Grammatical Info
            gram_info = sense.xpath("./grammatical-info")
            if gram_info:
                pos_val = gram_info[0].get('value')
                g.add((entry_uri, ONTOLEX.partOfSpeech, Literal(pos_val)))

    output_ttl = lift_path.replace('.lift', '.ttl')
    g.serialize(destination=output_ttl, format="turtle")
    print(f"✨ Serialization Complete: {output_ttl}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lift_to_lemon(sys.argv[1])
    else:
        print("Usage: python LIFT2lemon.py <file.lift>")
