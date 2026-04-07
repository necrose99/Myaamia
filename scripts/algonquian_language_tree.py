# algonquian_language_tree.py
ALGONQUIAN_FAMILY = {
    "algonquian": {
        "name": "Algonquian Language Family",
        "type": "language_family",
        "children": {
            # Plains Branch
            "plains": {
                "name": "Plains Algonquian",
                "type": "branch",
                "children": {
                    "bft": {"name": "Blackfoot", "type": "language"},
                    "arp": {"name": "Arapaho", "type": "language"},
                    "ats": {"name": "Gros Ventre", "type": "language"},
                    "chy": {"name": "Cheyenne", "type": "language"},
                }
            },
            # Central Branch (includes your focus languages)
            "central": {
                "name": "Central Algonquian",
                "type": "branch",
                "children": {
                    "men": {"name": "Menominee", "type": "language"},
                    "cre": {"name": "Cree", "type": "language"},
                    "csw": {"name": "Swampy Cree", "type": "dialect"},
                    "crj": {"name": "Southern East Cree", "type": "dialect"},
                    "atj": {"name": "Atikamekw", "type": "language"},
                    "pot": {"name": "Potawatomi", "type": "language"},
                    "oji": {"name": "Ojibwe", "type": "language"},
                    "otw": {"name": "Ottawa", "type": "dialect"},
                    "ciw": {"name": "Chippewa", "type": "dialect"},
                    "mia": {"name": "Miami-Illinois", "type": "language", "note": "⭐ YOUR FOCUS"},
                    "sac": {"name": "Meskwaki (Fox)", "type": "language", "note": "⭐ YOUR FOCUS"},
                    "kic": {"name": "Kickapoo", "type": "language"},
                    "sha": {"name": "Shawnee", "type": "language"},
                }
            },
            # Eastern Branch
            "eastern": {
                "name": "Eastern Algonquian",
                "type": "branch",
                "children": {
                    "mic": {"name": "Mi'kmaq", "type": "language"},
                    "abe": {"name": "Western Abenaki", "type": "language"},
                    "aaq": {"name": "Eastern Abnaki", "type": "language"},
                    "mal": {"name": "Maliseet-Passamaquoddy", "type": "language"},
                    "moo": {"name": "Mohegan-Pequot", "type": "language"},
                    "mua": {"name": "Munsee", "type": "language"},
                    "unm": {"name": "Unami", "type": "language"},
                }
            },
            # Proto-Language
            "proto": {
                "name": "Proto-Algonquian",
                "type": "proto_language",
                "children": {}
            }
        }
    }
}

def get_language_info(iso_code):
    """Get information about a specific Algonquian language."""
    # Recursive search function
    def search(node, code):
        if isinstance(node, dict):
            if node.get('type') == 'language' and code in node:
                return node[code]
            for key, child in node.items():
                if key != 'type' and key != 'name':
                    result = search(child, code)
                    if result:
                        return result
        return None
    
    return search(ALGONQUIAN_FAMILY, iso_code)

def get_family_tree():
    """Return the complete Algonquian language family tree."""
    return ALGONQUIAN_FAMILY
