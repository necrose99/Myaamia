#!/usr/bin/env python3
import os
import argparse
from rdflib import Graph, Namespace, RDF, OWL, RDFS

def clean_identifier(uri):
    """Sanitizes URIs and string data into safe Grammatical Framework (GF) tokens."""
    name = str(uri).split('#')[-1].split('/')[-1]
    cleaned = "".join(c for c in name if c.isalnum() or c == '_')
    # Force safe variable strings if characters get stripped completely
    return cleaned if cleaned else "token_entry"

def build_abstract(g, module_name, output_path):
    """Generates the GF Abstract Syntax mapping ontology entities directly from rdflib."""
    rules = [
        f"abstract {module_name} = {{\n",
        "  -- Baseline core categories",
        "  cat Class; Individual Class; Statement;\n"
    ]
    
    rules.append("  -- Classes")
    for cls in g.subjects(RDF.type, OWL.Class):
        name = clean_identifier(cls)
        if name and not name.startswith("owl_"):
            rules.append(f"  fun {name} : Class;")
            
    rules.append("\n  -- Individuals")
    for ind, cls in g.subject_objects(RDF.type):
        if (cls, RDF.type, OWL.Class) in g:
            ind_name = clean_identifier(ind)
            cls_name = clean_identifier(cls)
            if ind_name and cls_name:
                rules.append(f"  fun {ind_name} : Individual {cls_name};")

    rules.append("\n}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rules))
    print(f"[+] Abstract syntax generation complete: {output_path}")

def build_concrete(g, module_name, abstract_name, output_path):
    """Generates the GF Concrete Syntax parsing rdfs:label directly from the local file data store."""
    rules = [
        f"concrete {module_name} of {abstract_name} = open SyntaxEng, ParadigmsEng in {{\n",
        "  -- Linearization Judgements"
    ]
    oper_rules = ["\n  -- Operations / Morphological Paradigms"]
    
    ONTOLEX = Namespace("http://w3.org")
    RDFS = Namespace("http://w3.org")
    ALG = Namespace("http://example.org")
    
    mappings = {}
    total_count = 0
    
    # Target entities that have an rdfs:label assigned to map entries smoothly
    for entry in g.subjects(RDFS.label, None):
        
        # 1. Safely pull down your text label words
        written_rep = None
        for label in g.objects(entry, RDFS.label):
            # Only match strings, skip if it matches data property declarations
            if not str(label).startswith("http"):
                written_rep = str(label).strip()
                
        if not written_rep:
            continue
            
        # 2. Extract stable reference tags
        ref_name = None
        for sense in g.objects(entry, ONTOLEX.sense):
            for ilda_id in g.objects(sense, ALG.ildaId):
                ref_name = f"ilda_{ilda_id}"
                
        if not ref_name:
            ref_name = clean_identifier(entry)

        # 3. Clean variable tokens for GF layout formatting
        clean_word_tag = clean_identifier(written_rep).lower()
        var_base = f"{clean_word_tag}_N"
        
        if ref_name not in mappings:
            mappings[ref_name] = []
        mappings[ref_name].append(var_base)
        
        # Format the morphological layout parameter entry
        oper_rules.append(f"  oper {var_base} = mkN \"{written_rep}\";")
        total_count += 1
            
    # Assemble compiled structure maps
    for ref_name, variants in mappings.items():
        variant_str = ", ".join(variants)
        if len(variants) > 1:
            rules.append(f"  lin {ref_name} = variants {{ {variant_str} }};")
        else:
            rules.append(f"  lin {ref_name} = {variant_str};")
            
    rules.extend(oper_rules)
    rules.append("\n}")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rules))
    print(f"[+] Concrete syntax generation complete ({total_count} records processed): {output_path}")

def main():
    parser = argparse.ArgumentParser(description="lemon2gf: Streamlined RDF/TTL to GF Compiler")
    parser.add_argument("--ontology", required=True, help="Path to your ontology data file")
    parser.add_argument("--lexicon", required=True, help="Path to your lexicon data file")
    parser.add_argument("--domain", default="Myaamia", help="Base name for the GF Grammars")
    args = parser.parse_args()

    # Load via standard rdflib Graph parser to bypass owlready2 URI namespace issues
    print(f"[-] Parsing data file stream natively: {args.lexicon}")
    g = Graph()
    g.parse(args.lexicon, format="turtle")

    abs_file = f"{args.domain}.gf"
    cnc_file = f"{args.domain}Eng.gf"

    print("[-] Compiling Abstract Grammar Module...")
    build_abstract(g, args.domain, abs_file)
    
    print("[-] Compiling Concrete Grammar Module...")
    build_concrete(g, args.domain, f"{args.domain}Eng", cnc_file)
    print(f"[+] Done! Files successfully generated: {abs_file}, {cnc_file}")

if __name__ == "__main__":
    main()
