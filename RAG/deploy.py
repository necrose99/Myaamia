# Run as the ollama service account
sudo -u ollama voyager-deploy \
  --config algic_phoneme.yaml \
  --input /home/ollama/data/audio/blackfoot_field_recordings.mp3 \
  --output /home/ollama/data/sqlite/ipa_results.db
