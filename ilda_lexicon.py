#ilda_lexicon
import rdflib
g = rdflib.Graph()
g.parse(r"C:\Users\black\GitHub\Myaamia\mia_ilda_lexicon.ttl", format="turtle")

# Print the first 10 triples to see the exact structure
for i, (s, p, o) in enumerate(g):
    if i < 15:
        print(f"Subject: {s.split('#')[-1]} | Predicate: {p.split('#')[-1]} | Object: {o}")
    else:
        break