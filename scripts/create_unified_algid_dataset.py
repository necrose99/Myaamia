def create_unified_algid_dataset(mia_df, sauk_df, tmx_df):
    """
    Combine all available data sources:
    1. Miami-Illinois dictionary (word→definition)
    2. Sauk dictionary (word→definition)
    3. TMX parallel sentences
    """
    all_datasets = []
    
    # 1. Miami-Illinois dictionary pairs
    for _, row in mia_df.iterrows():
        if pd.notna(row.get('headword')) and pd.notna(row.get('definition')):
            # Word → Definition
            all_datasets.append({
                'source': row['headword'],
                'target': row['definition'],
                'source_lang': 'mia',
                'target_lang': 'en'
            })
            # Definition → Word
            all_datasets.append({
                'source': row['definition'],
                'target': row['headword'],
                'source_lang': 'en',
                'target_lang': 'mia'
            })
    
    # 2. Sauk dictionary pairs
    for _, row in sauk_df.iterrows():
        if pd.notna(row.get('headword')) and pd.notna(row.get('definition')):
            all_datasets.append({
                'source': row['headword'],
                'target': row['definition'],
                'source_lang': 'sauk',
                'target_lang': 'en'
            })
            all_datasets.append({
                'source': row['definition'],
                'target': row['headword'],
                'source_lang': 'en',
                'target_lang': 'sauk'
            })
    
    # 3. TMX parallel sentences
    # Group by language pairs
    for lang in tmx_df['source'].unique():
        lang_data = tmx_df[tmx_df['source'] == lang]
        en_data = tmx_df[tmx_df['source'] == 'en']
        
        # Simple matching (in practice, you'd match by context)
        for _, row in lang_data.iterrows():
            # Find English equivalent (simplified)
            en_match = en_data.sample(1).iloc[0] if not en_data.empty else None
            
            if en_match is not None:
                all_datasets.append({
                    'source': row['text'],
                    'target': en_match['text'],
                    'source_lang': lang,
                    'target_lang': 'en'
                })
                all_datasets.append({
                    'source': en_match['text'],
                    'target': row['text'],
                    'source_lang': 'en',
                    'target_lang': lang
                })
    
    return pd.DataFrame(all_datasets)

# Create unified dataset
unified_df = create_unified_algid_dataset(mia_df, sauk_df, df_tmx)
print(f"✅ Created unified dataset with {len(unified_df)} sentence pairs")
