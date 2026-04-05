# Allow the ollama user's services to run without an active session
sudo loginctl enable-linger ollama
# Run as the ollama user
sudo -u ollama -i
podman-compose up -d
podman generate systemd --name moltbook-bot --files
