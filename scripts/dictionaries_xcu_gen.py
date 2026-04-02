import lxml.etree as ET
import os

# Your 'Order of Battle' from the rack
algic_array = [
    "mia", "sac", "kic", "sha", "pot", "oji", "otw", "ciw", 
    "alq", "ojb", "cre", "men", "unm", "del", "bla", "arp"
]

def generate_xcu(dictionary_dir, output_file="dictionaries.xcu"):
    # XML Namespace setup for LibreOffice/OpenOffice
    ns_oor = "http://openoffice.org/2001/registry"
    attr_package = "{%s}package" % ns_oor
    attr_name = "{%s}name" % ns_oor
    attr_type = "{%s}type" % ns_oor

    root = ET.Element("node", {attr_package: "org.openoffice.Office", attr_name: "Linguistic"})
    service_manager = ET.SubElement(root, "node", {attr_name: "ServiceManager"})
    dictionaries = ET.SubElement(service_manager, "node", {attr_name: "Dictionaries"})

    count = 0
    for lang in algic_array:
        dic_file = f"{lang}.dic"
        aff_file = f"{lang}.aff"
        
        # Only register if the files actually exist on the rack
        if os.path.exists(os.path.join(dictionary_dir, dic_file)):
            node_name = f"HunSpellDic_{lang}"
            entry = ET.SubElement(dictionaries, "node", {attr_name: node_name, attr_type: "pkg:DictionaryService"})
            
            # Format: Locations (The files)
            prop_loc = ET.SubElement(entry, "prop", {attr_name: "Locations", attr_type: "oor:string-list"})
            val_loc = ET.SubElement(prop_loc, "value")
            val_loc.text = f"%origin%/dictionaries/{dic_file} %origin%/dictionaries/{aff_file}"
            
            # Format: Format (Hunspell)
            prop_fmt = ET.SubElement(entry, "prop", {attr_name: "Format", attr_type: "xs:string"})
            val_fmt = ET.SubElement(prop_fmt, "value")
            val_fmt.text = "DICT_HUNSPELL"
            
            # Format: Locales (The ISO Codes)
            prop_locales = ET.SubElement(entry, "prop", {attr_name: "Locales", attr_type: "oor:string-list"})
            val_locales = ET.SubElement(prop_locales, "value")
            val_locales.text = lang
            
            count += 1

    # Write out the Registry
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True, pretty_print=True)
    print(f"✅ Generated {output_file} with {count} Algic language mappings.")

if __name__ == "__main__":
    # Point this to where your .dic files live
    generate_xcu('dicts')
