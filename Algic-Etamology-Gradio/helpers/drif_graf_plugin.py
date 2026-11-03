#!/usr/bin/env python3
"""
drift_plugin.py - Adversarial Domain Drift Detection for Algic Dictionary Dumps
Integrated into the Algic-Etamology-Flask framework.
"""

import sqlite3
import pandas as pd
import numpy as np
import ety
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

class DriftAnalyzerPlugin:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts structural features from lexical tokens using ety checks 
        and structural string profiles.
        """
        features = []
        for _, row in df.iterrows():
            form = str(row.get('form', ''))
            gloss = str(row.get('gloss_en', ''))
            proto = str(row.get('proto_form', ''))
            morph = str(row.get('morph_seg', ''))
            
            # 1. Base morphological complexity
            word_len = len(form)
            seg_count = len(morph.split('-')) if morph and morph != 'None' else 1
            has_proto = 1 if (proto and proto != 'None') else 0
            
            # 2. Etymological footprint of gloss/loan definition mappings via ety
            gloss_words = gloss.split()
            ie_origin_count = 0
            if gloss_words:
                for w in gloss_words:
                    try:
                        if ety.origins(w):
                            ie_origin_count += 1
                    except Exception:
                        pass
                ie_ratio = ie_origin_count / len(gloss_words)
            else:
                ie_ratio = 0.0

            features.append({
                'word_length': word_len,
                'segmentation_depth': seg_count,
                'has_reconstructed_proto': has_proto,
                'gloss_ie_influence': ie_ratio
            })
        return pd.DataFrame(features)

    def load_baseline_from_db(self, lang: str, limit: int = 1000) -> pd.DataFrame:
        """Loads historical or baseline language entries from the database."""
        query = """
            SELECT form, gloss_en, proto_form, morph_seg 
            FROM entries 
            WHERE lang = ? 
            ORDER BY created_at ASC LIMIT ?
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(lang, limit))
        return df

    def calculate_dump_drift(self, baseline_df: pd.DataFrame, new_entries: list) -> dict:
        """
        Computes the drift index between the baseline DB matrix 
        and an incoming dictionary dump using a Random Forest Domain Classifier.
        """
        if baseline_df.empty or not new_entries:
            return {"drift_index": 0.50, "status": "insufficient_data"}
            
        df_target = pd.DataFrame(new_entries)
        
        # Build vector spaces
        X_base = self._extract_features(baseline_df)
        X_target = self._extract_features(df_target)
        
        # Label domain targets: Baseline = 0, Incoming Dump = 1
        X_base['is_target'] = 0
        X_target['is_target'] = 1
        
        combined = pd.concat([X_base, X_target], ignore_index=True)
        feature_cols = ['word_length', 'segmentation_depth', 'has_reconstructed_proto', 'gloss_ie_influence']
        
        X = combined[feature_cols]
        y = combined['is_target']
        
        # Fit Domain Classifier
        clf = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
        
        # Cross-validated ROC-AUC serves as the drift measurement indicator
        try:
            scores = cross_val_score(clf, X, y, cv=3, scoring='roc_auc')
            drift_auc = float(np.mean(scores))
        except Exception:
            drift_auc = 0.50
            
        # Normalize: 0.5 means identical distribution, 1.0 means total distinct subsets
        normalized_drift = max(0.0, (drift_auc - 0.5) * 2)
        
        return {
            "drift_index": drift_auc,
            "normalized_drift_magnitude": normalized_drift,
            "metrics": {
                "base_avg_len": float(X_base['word_length'].mean()),
                "target_avg_len": float(X_target['word_length'].mean()),
                "base_ie_influence": float(X_base['gloss_ie_influence'].mean()),
                "target_ie_influence": float(X_target['gloss_ie_influence'].mean()),
            }
        }
