# Allow the ollama user's services to run without an active session
sudo loginctl enable-linger ollama
# Run as the ollama user
sudo -u ollama -i
podman-compose up -d
podman generate systemd --name moltbook-bot --files
mkdir -p ~/.config/systemd/user/
mv container-moltbook-bot.service ~/.config/systemd/user/
systemctl --user enable --now container-moltbook-bot.service

# Create a system user with a home directory
sudo useradd -r -m -d /home/ollama -s /bin/bash ollama

# Set a password if you want to SSH directly as 'ollama'
sudo passwd ollama

# Create the data structure for the stack
sudo mkdir -p /home/ollama/data/{ollama_logs,sqlite,tmx,scripts}
sudo chown -R ollama:ollama /home/ollama/data
