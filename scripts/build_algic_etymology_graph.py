def build_algic_etymology_graph():
    """Build a graph showing relationships between Algic languages."""
    import networkx as nx
    from collections import defaultdict
    
    # Collect all words
    all_words = []
    
    # From TMX
    for _, row in df_tmx.iterrows():
        all_words.append((row['source'], row['text']))
    
    # From dictionaries (simplified)
    for _, row in mia_df.iterrows():
        if pd.notna(row.get('headword')):
            all_words.append(('mia', row['headword']))
    for _, row in sauk_df.iterrows():
        if pd.notna(row.get('headword')):
            all_words.append(('sauk', row['headword']))
    
    # Build graph
    G = nx.Graph()
    G.add_nodes_from(all_words)
    
    # Find cognates (simplified)
    for i, (lang1, word1) in enumerate(all_words):
        for j, (lang2, word2) in enumerate(all_words[i+1:], i+1):
            if lang1 != lang2:  # Only cross-language edges
                # Simple phonetic similarity
                from difflib import SequenceMatcher
                similarity = SequenceMatcher(None, word1, word2).ratio()
                
                if similarity > 0.6:  # Threshold for cognates
                    G.add_edge(
                        (lang1, word1), 
                        (lang2, word2), 
                        weight=similarity
                    )
    
    return G

def visualize_etymology(G):
    """Create an interactive etymology visualization."""
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # Color by language
    colors = []
    for node in G.nodes():
        if node[0] == 'mia':
            colors.append('blue')
        elif node[0] == 'sauk':
            colors.append('green')
        elif node[0] == 'en':
            colors.append('red')
        else:
            colors.append('gray')
    
    nx.draw_networkx_nodes(
        G, pos, 
        node_color=colors, 
        node_size=100,
        alpha=0.8,
        cmap=plt.cm.Set1
    )
    
    nx.draw_networkx_edges(
        G, pos, 
        alpha=0.3, 
        width=1
    )
    
    nx.draw_networkx_labels(
        G, pos, 
        font_size=8, 
        font_family="Arial"
    )
    
    plt.title("Algic Language Cognate Network")
    plt.axis("off")
    plt.savefig("algic_etymology.png", dpi=300, bbox_inches="tight")
    plt.show()
