# !/bin/bash
# export_all.sh

echo "🚀 Exporting all formats..."

# Export OLAC data
echo "📄 Exporting OLAC TMX..."
python olac_exporter.py export-tmx \
    --db olac_data.db \
    --output olac_export.tmx \
    --source esx \
    --target eng

echo "📄 Exporting OLAC EAF..."
python olac_exporter.py export-eaf \
    --db olac_data.db \
    --output olac_elicitation.eaf \
    --language esx

# Export Proto-Algonquian data
echo "📄 Exporting Proto-Algonquian TMX..."
python proto_exporter.py export-tmx \
    --db proto_algonquian.db \
    --output proto_export.tmx \
    --source proto-alg \
    --target eng

echo "📄 Exporting Proto-Algonquian FLEX..."
python proto_exporter.py export-flex \
    --db proto_algonquian.db \
    --output proto_lexicon.flex

echo "✅ All exports complete!"
echo "📁 Check current directory for exported files"
