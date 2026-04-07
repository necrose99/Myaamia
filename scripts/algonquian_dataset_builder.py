# algonquian_dataset_builder.py
import pandas as pd
from datasets import DatasetDict
from pathlib import Path

class AlgonquianDatasetBuilder:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Load existing data
        self.mia_df = self._load_csv("mia_dictionary.csv")
        self.sauk_df = self._load_csv("sauk_dictionary.csv")
        self.tmx_df = self._load_tmx("Algic.tmx")
        
        # Initialize other language dataframes
        self.languages = {}
        
    def _load_csv(self, filename):
        """Load CSV dictionary if it exists."""
        filepath = self.data_dir / filename
        if filepath.exists():
            return pd.read_csv(filepath)
        return pd.DataFrame()
    
    def _load_tmx(self, filename):
        """Load and parse TMX file."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            # Download from GitHub
            import requests
            url = f"https://github.com/necrose99/Myaamia/raw/master/target/{filename}"
            response = requests.get(url)
            with open(filepath, 'wb') as f:
                f.write(response.content)
        
        # Parse TMX
        return self._parse_tmx(filepath)
    
    def _parse_tmx(self, filepath):
        """Parse TMX XML into DataFrame."""
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        entries = []
        for tu in root.findall('.//tu'):
            for tuv in tu.findall('.//tuv'):
                lang = tuv.get('{http://www.w3.org/XML/1998/namespace}lang', '')
                seg = tuv.find('seg')
                if seg is not None and seg.text:
                    entries.append({
                        'language': lang,
                        'text': seg.text.strip(),
                        'source': lang.split('-')[0]
                    })
        
        return pd.DataFrame(entries)
    
    def add_language_data(self, iso_code, df):
        """Add data for a specific language."""
        self.languages[iso_code] = df
    
    def build_unified_dataset(self):
        """Build a unified dataset from all sources."""
        all_datasets = []
        
        # 1. Miami-Illinois dictionary pairs
        for _, row in self.mia_df.iterrows():
            if pd.notna(row.get('headword')) and pd.notna(row.get('definition')):
                all_datasets.append({
                    'source': row['headword'],
                    'target': row['definition'],
                    'source_lang': 'mia',
                    'target_lang': 'en'
                })
                all_datasets.append({
                    'source': row['definition'],
                    'target': row['headword'],
                    'source_lang': 'en',
                    'target_lang': 'mia'
                })
        
        # 2. Sauk dictionary pairs
        for _, row in self.sauk_df.iterrows():
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
        for _, row in self.tmx_df.iterrows():
            # Simple matching (in practice, you'd match by context)
            # For now, treat each TMX entry as both source and target
            all_datasets.append({
                'source': row['text'],
                'target': row['text'],  # Placeholder
                'source_lang': row['source'],
                'target_lang': 'en'  # Assume English target for now
            })
        
        # 4. Add other language data if available
        for iso_code, df in self.languages.items():
            for _, row in df.iterrows():
                if pd.notna(row.get('headword')) and pd.notna(row.get('definition')):
                    all_datasets.append({
                        'source': row['headword'],
                        'target': row['definition'],
                        'source_lang': iso_code,
                        'target_lang': 'en'
                    })
                    all_datasets.append({
                        'source': row['definition'],
                        'target': row['headword'],
                        'source_lang': 'en',
                        'target_lang': iso_code
                    })
        
        return pd.DataFrame(all_datasets)
    
    def create_datasets(self, df, train_ratio=0.8):
        """Split into train/val/test datasets."""
        from datasets import Dataset, DatasetDict
        
        train_size = int(len(df) * train_ratio)
        val_size = int((len(df) - train_size) / 2)
        test_size = len(df) - train_size - val_size
        
        train_df = df.iloc[:train_size]
        val_df = df.iloc[train_size:train_size+val_size]
        test_df = df.iloc[train_size+val_size:]
        
        return DatasetDict({
            'train': Dataset.from_dict(train_df.to_dict('records')),
            'validation': Dataset.from_dict(val_df.to_dict('records')),
            'test': Dataset.from_dict(test_df.to_dict('records'))
        })
