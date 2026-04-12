import sys
import os
import glob
from datetime import datetime
from saxonche import PySaxonProcessor

# Your Order of Battle for filtering
algic_array = [
    "alg-x-proto", "bla", "arp", "ats", "chy", "bft",
    "men", "cre", "csw", "crj", "atj", "nsk", "moos", "crm", 
    "pot", "oji", "otw", "ciw", "alq", "ojb", "ojg", "ojs", 
    "mia", "sac", "kic", "sha", "mic", "abe", "aaq", "mal", 
    "moo", "mua", "unm", "wamp", "mas", "nrn", "qpi", "nnt", 
    "pow", "pmk", "psk", "mjy", "wiy", "yur", "en-US", "Latin", "es_mx", "fr"
]

def run_lift_transformation(tmx_file, xsl_file):
    output_lift = tmx_file.replace('.tmx', '.lift')
    
    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        
        # Compile your XSLT (supports XSLT 2.0 grouping)
        executable = xsltproc.compile_xslt_from_file(xsl_file)
        
        # Set the source TMX
        source = proc.parse_xml(xml_file_name=tmx_file)
        
        # Apply transformation to rebuild LIFT hierarchy
        result = executable.transform_to_string(xdm_node=source)
        
        with open(output_lift, 'w', encoding='utf-8') as f:
            f.write(result)
            
    print(f"✅ Transmogrified {tmx_file} into {output_lift}")

if __name__ == "__main__":
    XSL_PATH = "tmx-to-lift.xsl"
    
    # Handle Windows wildcard expansion
    args = sys.argv[1:] if len(sys.argv) > 1 else ["*.tmx"]
    files = []
    for arg in args:
        files.extend(glob.glob(arg))
        
    for f in files:
        if os.path.exists(f):
            run_lift_transformation(f, XSL_PATH)