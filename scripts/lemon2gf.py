#!/usr/bin/env python3
import os
import argparse
from owlready2 import World
from rdflib import Namespace, RDF, OWL, RDFS

# Common Namespace Constants
LEMON = Namespace("http://lemon-model.net")
LEXINFO = Namespace("http://lexinfo.net")

def clean_identifier(uri):
    """Sanitizes URIs into safe Grammatical Framework (GF) identifiers."""
    name = str(uri).split('#')[-1].split('/')[-1]
    return "".join(c for c in name if c.isalnum() or c == '_')

def build_abstract(world, module_name, output_path):
    """Generates the GF Abstract Syntax mapping ontology entities."""
    rules = [
        f"abstract {module_name} = {{\n",
        "  -- Baseline core categories",
        "  cat Class; Individual Class; Statement;\n"
    ]
    
    # 1. Map Classes
    rules.append("  -- Classes")
    for cls in world.sparql("SELECT ?c WHERE { ?c a owl:Class . FILTER(ISIRI(?c)) }"):
        name = clean_identifier(cls[0])
        if name:
            rules.append(f"  fun {name} : Class;")
            
    # 2. Map Individuals
    rules.append("\n  -- Individuals")
    ind_query = """
        SELECT ?ind ?cls WHERE { 
            ?ind a ?cls . 
            ?cls a owl:Class .
            FILTER(ISIRI(?ind) && ISIRI(?cls))
        }
    """
    for ind, cls in world.sparql(ind_query):
        ind_name = clean_identifier(ind)
        cls_name = clean_identifier(cls)
        if ind_name and cls_name:
            rules.append(f"  fun {ind_name} : Individual {cls_name};")

    # 3. Map Object Properties
    rules.append("\n  -- Object Properties")
    for prop in world.sparql("SELECT ?p WHERE { ?p a owl:ObjectProperty . }"):
        p_name = clean_identifier(prop[0])
        # Leverage rdflib binding within the world graph to grab domain/range
        g = world.as_rdflib_graph()
        domain = next(g.objects(prop[0], RDFS.domain), OWL.Thing)
        range_ = next(g.objects(prop[0], RDFS.range), OWL.Thing)
        
        dom_name = clean_identifier(domain) if domain != OWL.Thing else "Thing"
        rng_name = clean_identifier(range_) if range_ != OWL.Thing else "Thing"
        
        if p_name:
            rules.append(f"  fun {p_name} : Individual {dom_name} -> Individual {rng_name} -> Statement;")

    # 4. Map Datatype Properties
    rules.append("\n  -- Datatype Properties")
    for prop in world.sparql("SELECT ?p WHERE { ?p a owl:DatatypeProperty . }"):
        p_name = clean_identifier(prop[0])
        g = world.as_rdflib_graph()
        domain = next(g.objects(prop[0], RDFS.domain), OWL.Thing)
        range_ = next(g.objects(prop[0], RDFS.range), "xsddouble")
        
        dom_name = clean_identifier(domain) if domain != OWL.Thing else "Thing"
        rng_name = clean_identifier(range_).lower()
        
        if p_name:
            rules.append(f"  fun {p_name} : Individual {dom_name} -> {rng_name} -> Statement;")

    rules.append("\n}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rules))

def build_concrete(world, module_name, abstract_name, output_path):
    """Generates the GF Concrete Syntax mapping Lexicon words."""
    rules = [
        f"concrete {module_name} of {abstract_name} = open SyntaxEng, ParadigmsEng in {{\n",
        "  -- Linearization Judgements"
    ]
    oper_rules = ["\n  -- Operations / Morphological Paradigms"]
    
    # Query matching lemon lexical entries with their targeted ontology references
    lemon_query = """
    PREFIX lemon: <http://lemon-model.net>
    PREFIX lexinfo: <http://lexinfo.net>
    
    SELECT ?reference ?writtenRep ?pluralRep WHERE {
        ?entry a lemon:LexicalEntry ;
               lemon:sense [ lemon:reference ?reference ] ;
               lemon:canonicalForm [ lemon:writtenRep ?writtenRep ] .
        OPTIONAL { ?entry lemon:otherForm [ lemon:writtenRep ?pluralRep ; lexinfo:number lexinfo:plural ] }
    }
    """
    
    mappings = {}
    for ref, written_rep, plural_rep in world.sparql(lemon_query):
        ref_name = clean_identifier(ref)
        var_base = f"{written_rep.lower()}_N"
        
        if ref_name not in mappings:
            mappings[ref_name] = []
        mappings[ref_name].append(var_base)
        
        if plural_rep:
            oper_rules.append(f"  oper {var_base} = mkN \"{written_rep}\" \"{plural_rep}\";")
        else:
            oper_rules.append(f"  oper {var_base} = mkN \"{written_rep}\";")
            
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

def main():
    parser = argparse.ArgumentParser(description="lemon2gf: Transform Ontology + Lemon Lexicon into GF Grammars")
    parser.add_argument("--ontology", required=True, help="Path to the OWL/TTL Ontology file")
    parser.add_argument("--lexicon", required=True, help="Path to the Lemon Lexicon TTL file")
    parser.add_argument("--domain", default="TravelDomain", help="Base name for the GF Grammars")
    args = parser.parse_args()

    # Load resources into a unified Owlready2 Quadstore
    world = World()
    print(f"Loading Ontology: {args.ontology}")
    world.get_ontology(args.ontology).load()
    print(f"Loading Lexicon: {args.lexicon}")
    world.get_ontology(args.lexicon).load()

    # Define module names and file outputs
    abs_name = args.domain
    cnc_name = f"{args.domain}Eng"
    abs_file = f"{abs_name}.gf"
    cnc_file = f"{cnc_name}.gf"

    print("Compiling Abstract Grammar...")
    build_abstract(world, abs_name, abs_file)
    print("Compiling Concrete Grammar...")
    build_concrete(world, cnc_name, abs_name, cnc_file)
    print(f"Done! Output generated: {abs_file}, {cnc_file}")

if __name__ == "__main__":
    main()
