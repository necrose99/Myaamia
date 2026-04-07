# !/usr/bin/env bash
# algonquian_pipeline.sh - Complete Algonquian language revitalization pipeline

# 1. Download and extract data
echo "📥 Downloading Algic TMX file..."
wget "https://github.com/necrose99/Myaamia/raw/master/target/Algic.tmx" -O data/Algic.tmx

echo "📥 Loading Miami-Illinois dictionary (from previous work)..."
# Assuming mia_dictionary.csv exists

echo "📥 Loading Sauk dictionary (from PDF extraction)..."
# Assuming sauk_dictionary.csv exists

# 2. Build dataset
echo "🔗 Building unified Algonquian dataset..."
python algonquian_dataset_builder.py

# 3. Train model
echo "🤖 Training Algonquian multilingual model..."
python algonquian_multilingual_trainer.py

# 4. Build etymology graph
echo "🌳 Building Algonquian etymology network..."
python algonquian_etymology.py

# 5. Launch web app
echo "🌐 Launching Algonquian language helper..."
python algonquian_translator_app.py
