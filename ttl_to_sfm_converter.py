import re
import sys

def convert_ttl_to_sfm(ttl_text):
    """
    A basic parser to convert custom Turtle (TTL) linguistic triples to SIL SFM format.
    """
    # Simple extraction of literals from custom predicates
    entries = re.findall(r':(\w+)\s+rdf:type\s+:Lexeme\s*\;(.*?)\.', ttl_text, re.DOTALL)
    
    sfm_blocks = []
    for lexeme_id, body in entries:
        block = [f"\\lx {lexeme_id}"]
        
        pos = re.search(r':partOfSpeech\s+"([^"]+)"', body)
        gloss = re.search(r':glossEnglish\s+"([^"]+)"', body)
        ex_vern = re.search(r':exampleVernacular\s+"([^"]+)"', body)
        ex_eng = re.search(r':exampleEnglish\s+"([^"]+)"', body)
        
        if pos: block.append(f"\\ps {pos.group(1)}")
        if gloss: block.append(f"\\ge {gloss.group(1)}")
        if ex_vern: block.append(f"\\xv {ex_vern.group(1)}")
        if ex_eng: block.append(f"\\xe {ex_eng.group(1)}")
        
        sfm_blocks.append("\n".join(block))
        
    return "\n\n".join(sfm_blocks)

if __name__ == "__main__":
    # Example usage
    sample_ttl = """
    :miami rdf:type :Lexeme ;
        :partOfSpeech "n" ;
        :glossEnglish "Miami (person, language, or place)" ;
        :exampleVernacular "nila myaamionki ondji." ;
        :exampleEnglish "I am from the Miami nation." .
    """
    print(convert_ttl_to_sfm(sample_ttl))
