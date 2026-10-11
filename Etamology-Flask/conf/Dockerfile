FROM python:3-alpine
LABEL maintainer="Niko Schmuck <niko@nava.de>"

# 1. Install System Dependencies
RUN apk add --no-cache \
    tini \
    lighttpd \
    openssl \
    curl \
    tar \
    zstd \
    zstd-dev \
    certbot \
    build-base \
    openldap-dev \
    python3-dev \
    libffi-dev \
    git \
    sqlite-dev \
    libxml2-dev \
    libxslt-dev \
    gcc \
    musl-dev

# 2. Setup Application Directory
WORKDIR /var/www/Etamology

# 3. Download and Decompress the Custom Repository Archive Payload
ADD https://github.com/necrose99/Myaamia/raw/master/Etamology-Flask/Etamology-Flask.ztar.xz ./Etamology.tar.xz
RUN tar -I zstd -xf Etamology.tar.xz --strip-components=1 && rm Etamology.tar.xz

# 4. Install Application Requirements
RUN pip install --no-cache-dir \
    gunicorn \
    flask \
    flask-ldap3 \
    pyglossary \
    translate-toolkit \
    ety \
    pysqlite3-binary \
    zstandard \
    flask-ldap3-login \
    flask-ad-auth \
    rdflib \
    requests \
    lxml \
     fonttools[woff2]
# 5. Base System Configuration Folders
RUN mkdir -p /etc/lighttpd/certs /var/www/Etamology/.well-known/acme-challenge

# 5a. Generate the Tiny Shell Cron Runner
COPY <<'EOF' /usr/local/bin/renew.sh
#!/bin/sh
echo "[$(date)] Checking certificate status..."

# Run certbot check using the webroot challenge directory
certbot renew --webroot -w /var/www/Etamology \
    --deploy-hook "echo '[$(date)] New certificate deployed. Reloading Lighttpd...'; pkill -HUP lighttpd" \
    --non-interactive \
    --agree-tos

echo "[$(date)] Verification check complete."
EOF

RUN chmod +x /usr/local/bin/renew.sh

# 5b. Generate Hardened Dynamic Lighttpd Reverse-Proxy Configuration
COPY <<EOF /etc/lighttpd/lighttpd.conf
server.modules += ( "mod_proxy", "mod_openssl", "mod_alias", "mod_setenv" )

server.document-root = "/var/www/Etamology"
server.port = 80
server.username = "lighttpd"
server.groupname = "lighttpd"

# Direct ACME validation path mapping
alias.url = ( "/.well-known/acme-challenge/" => "/var/www/Etamology/.well-known/acme-challenge/" )

# Standard Port 80 Proxy Handling for app.lan / duckdns / fallback hosts
\$HTTP["host"] =~ ".*" {
    # Exclude letsencrypt challenge paths from reverse proxy matching rules
    \$HTTP["url"] !~ "^/\\.well-known/" {
        proxy.server = ( "" => (( "host" => "127.0.0.1", "port" => 5000 )))
    }
}

# Hardened SSL Engine Profile (Port 443)
\$SERVER["socket"] == ":443" {
    ssl.engine                  = "enable"
    ssl.pemfile                 = "/etc/letsencrypt/live/://yourdomain.com"
    ssl.privkey                 = "/etc/letsencrypt/live/://yourdomain.com"
    
    # Advanced Security Hardening Headers
    setenv.add-environment      = ( "HTTPS" => "on" )
    setenv.add-response-header  = ( "Strict-Transport-Security" => "max-age=15768000;" )
    
    # BEAST Mitigation Layer Configuration
    ssl.openssl.ssl-conf-cmd    = ("MinProtocol" => "TLSv1.2")
    ssl.cipher-list             = "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305"
    ssl.honor-cipher-order      = "enable"
    ssl.disable-client-renegotiation = "enable"
    ssl.use-compression         = "disable"

    # Forward Secure Traffic straight down into your Gunicorn Server engine
    \$HTTP["url"] !~ "^/\\.well-known/" {
        proxy.server = ( "" => (( "host" => "127.0.0.1", "port" => 5000 )))
    }
}
EOF

# 6. Open Up Network Interfaces
EXPOSE 80 443 5000

# 7. Lifecycle Initialization via Container Engine Supervisor (Tini)
ENTRYPOINT ["/sbin/tini", "--"]

# Run Gunicorn + internal micro check-loop + foreground web server process engine
CMD sh -c "\
    gunicorn --bind 127.0.0.1:5000 algic_ety_applet_v3:app & \
    while :; do /usr/local/bin/renew.sh; sleep 12h; done & \
    exec lighttpd -D -f /etc/lighttpd/lighttpd.conf"
