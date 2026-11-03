#!/usr/bin/env bash
set -e

COMPOSE_FILE="docker-compose.yaml"
ENV_FILE=".env"

echo "===================================================="
echo " Starting Etamology-Flask Deployment Engine         "
echo "===================================================="

# 1. Automated Environment (.env) Initializer Block
if [ ! -f "$ENV_FILE" ]; then
    echo "[!] Configuration template ($ENV_FILE) not found."
    echo "    Generating default production variables..."

    # Generate a cryptographically secure random password for the admin
    RANDOM_ADMIN_PASS=$(openssl rand -base64 12 2>/dev/null || echo "EtamologyPass123!")

    cat <<EOF > "$ENV_FILE"
# ====================================================
# Etamology-Flask Runtime Environment Variables
# ====================================================

# Host Domain Name configuration
MY_DOMAIN=localhost
CERTBOT_EMAIL=admin@localhost.local

# Default Web Admin Credentials (Used by build.py on initialization)
ADMIN_USER=admin
ADMIN_PASSWORD=${RANDOM_ADMIN_PASS}

# Application States
FLASK_ENV=production
SQLITE_DB_PATH=/var/www/Etamology/data/etamology.db
EOF
    echo "[✔] Saved new configurations to $ENV_FILE"
    echo "    ------------------------------------------------"
    echo "    DEFAULT ADMIN USER : admin"
    echo "    DEFAULT PASSWORD   : ${RANDOM_ADMIN_PASS}"
    echo "    ------------------------------------------------"
    echo "    (You can change these values inside the .env file anytime)"
fi

# 2. Detect Container Engine
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "[✔] Docker Compose engine detected."
    echo "Launching container build layers..."
    docker compose up --build -d

elif command -v podman &> /dev/null && command -v podman-compose &> /dev/null; then
    echo "[✔] Podman and Podman-Compose tools detected."
    
    # Podman Rootless port 80/443 safeguard hint
    if [ "$EUID" -ne 0 ]; then
        echo "[!] WARNING: You are running Podman in Rootless mode."
        echo "    If ports 80/443 fail to bind, configure unprivileged ports via:"
        echo "    'sudo sysctl net.ipv4.ip_unprivileged_port_start=80'"
    fi

    echo "Launching podman build layers..."
    podman-compose up --build -d

else
    echo "[✘] CRITICAL: Neither Docker Compose nor Podman Compose was found."
    echo "    Please install docker-compose or podman-compose to deploy this app."
    exit 1
fi

echo "===================================================="
echo "[✔] Deployment deployment command completed successfully!"
echo "===================================================="
