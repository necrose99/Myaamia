import sys
import os
import glob
from dataclasses import dataclass, field
from typing import List, Optional, Any
import xml.etree.ElementTree as ET
from saxonche import PySaxonProcessor

# --- Dataclasses for XSLT Structure Analysis ---

@dataclass
class XslTemplate:
    [span_5](start_span)[span_6](start_span)"""Represents a template match or named template in the XSLT[span_5](end_span)[span_6](end_span)."""
    match: Optional[str] = None
    name: Optional[str] = None
    content: List[Any] = field(default_factory=list)

    @classmethod
    def from_xml(cls, elem: ET.Element, ns: dict) -> 'XslTemplate':
        return cls(
            match=elem.get('match'),
            name=elem.get('name')
        )

@dataclass
class XslStylesheet:
    [span_7](start_span)[span_8](start_span)"""Represents the root XSL stylesheet and its global parameters[span_7](end_span)[span_8](end_span)."""
    version: str = "2.0"
    params: dict = field(default_factory=dict)
    templates: List[XslTemplate] = field(default_factory=list)

    @classmethod
    def from_xml(cls, root_elem: ET.Element) -> 'XslStylesheet':
        ns = {'xsl': 'http://www.w3.org/1999/XSL/Transform'}
        instance = cls(version=root_elem.get('version', '2.0'))
        
        # [span_9](start_span)Map parameters like lift-version and source-lang[span_9](end_span)
        for param in root_elem.findall('xsl:param', ns):
            name = param.get('name')
            select = param.get('select')
            instance.params[name] = select
            
        # [span_10](start_span)[span_11](start_span)Map templates for entry and sense reconstruction[span_10](end_span)[span_11](end_span)
        for template in root_elem.findall('xsl:template', ns):
            instance.templates.append(XslTemplate.from_xml(template, ns))
            
        return instance

# --- Transformation Logic ---

# Your "Order of Battle" for Algic Languages
ALGIC_ARRAY = [
    "alg-x-proto", "bla", "arp", "ats", "chy", "bft",
    "men", "cre", "csw", "crj", "atj", "nsk", "moos", "crm", 
    "pot", "oji", "otw", "ciw", "alq", "ojb", "ojg", "ojs", 
    "mia", "sac", "kic", "sha", "mic", "abe", "aaq", "mal", 
    "moo", "mua", "unm", "wamp", "mas", "nrn", "qpi", "nnt", 
    "pow", "pmk", "psk", "mjy", "wiy", "yur", "en-US", "Latin", "es_mx", "fr"
]

def run_lift_transformation(tmx_file, xsl_file):
    """
    [span_12](start_span)Uses SaxonC-HE to apply XSLT 2.0 grouping logic[span_12](end_span).
    [span_13](start_span)[span_14](start_span)Reconstructs LIFT hierarchy from flat TMX TUs[span_13](end_span)[span_14](end_span).
    """
    output_lift = tmx_file.replace('.tmx', '.lift')
    
    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        
        # [span_15](start_span)Compile XSLT to support <xsl:for-each-group>[span_15](end_span)
        executable = xsltproc.compile_xslt_from_file(xsl_file)
        
        # Parse source TMX
        source = proc.parse_xml(xml_file_name=tmx_file)
        
        # [span_16](start_span)[span_17](start_span)Apply transformation to rebuild entry/sense hierarchy[span_16](end_span)[span_17](end_span)
        result = executable.transform_to_string(xdm_node=source)
        
        with open(output_lift, 'w', encoding='utf-8') as f:
            f.write(result)
            
    print(f"✅ Transmogrified {tmx_file} into {output_lift}")

# --- Main Execution ---

if __name__ == "__main__":
    # Ensure tmx-to-lift.xsl is in the same directory
    XSL_PATH = "tmx-to-lift.xsl"
    
    # Handle Windows/PowerShell wildcard expansion
    args = sys.argv[1:] if len(sys.argv) > 1 else ["*.tmx"]
    files = []
    for arg in args:
        files.extend(glob.glob(arg))
        
    if not files:
        print("❌ No TMX files found. Check your directory or file names.")
    else:
        for f in files:
            if os.path.exists(f):
                run_lift_transformation(f, XSL_PATH)
