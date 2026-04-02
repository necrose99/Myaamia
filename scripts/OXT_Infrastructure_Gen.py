import lxml.etree as ET
import os

def generate_manifest(output_dir="META-INF"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    root = ET.Element("manifest", {
        "{http://openoffice.org/2001/manifest}version": "1.2",
        "xmlns:manifest": "http://openoffice.org/2001/manifest"
    })
    
    # Register the dictionaries.xcu
    file_entry = ET.SubElement(root, "manifest:file-entry", {
        "manifest:full-path": "dictionaries.xcu",
        "manifest:media-type": "application/vnd.sun.star.configuration-data"
    })
    
    tree = ET.ElementTree(root)
    tree.write(os.path.join(output_dir, "manifest.xml"), encoding="utf-8", xml_declaration=True, pretty_print=True)

def generate_description(output_file="description.xml"):
    root = ET.Element("description", {
        "xmlns": "http://openoffice.org/2001/description",
        "xmlns:d": "http://openoffice.org/2001/description",
        "xmlns:xlink": "http://www.w3.org/1999/xlink"
    })
    
    identifier = ET.SubElement(root, "identifier", value="org.algic.nilla.myaamiaki.spellcheck")
    version = ET.SubElement(root, "version", value="1.0.0")
    
    display_name = ET.SubElement(root, "display-name")
    name_text = ET.SubElement(display_name, "value", lang="en")
    name_text.text = "Algic Language Suite (Nilla Myaamiaki Edition)"
    
    publisher = ET.SubElement(root, "publisher")
    pub_text = ET.SubElement(publisher, "value", lang="en")
    pub_text.text = "Wabash Valley Sovereignty Node"
    
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True, pretty_print=True)

if __name__ == "__main__":
    generate_manifest()
    generate_description()
    print("✅ META-INF/manifest.xml and description.xml are ready for the rack.")
