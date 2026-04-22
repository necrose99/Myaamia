import os
from pympi.Elan import Eaf
import pandas as pd

eaf_dir = "eaf_output"
data = []

for f in os.listdir(eaf_dir):
    if f.endswith('.eaf'):
        eaf = Eaf(os.path.join(eaf_dir, f))
        txt = eaf.get_annotation_data_for_tier("Transcription-MIA")
        ipa = eaf.get_annotation_data_for_tier("Phoneme-MIA")
        if txt and ipa:
            data.append({"myaamia": txt[0][2], "ipa": ipa[0][2]})

df = pd.DataFrame(data)
df.to_csv("myaamia_gold_standard.csv", index=False)
print(f"✅ Exported {len(df)} perfect pairs for the next bake.")