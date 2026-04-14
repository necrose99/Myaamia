#!/bin/bash
# Path to the domain folder in letsencrypt
# /etc/letsencrypt/renewal-hooks/deploy/lighttpd.sh 

# Path to the concatenated PEM file Lighttpd uses
LIGHTTPD_PEM="/etc/lighttpd/ssl/example.com/combined.pem"

# Combine fullchain and privkey
cat "$RENEWED_LINEAGE/fullchain.pem" "$RENEWED_LINEAGE/privkey.pem" > "$LIGHTTPD_PEM"

# Set proper permissions
chown lighttpd:lighttpd "$LIGHTTPD_PEM"
chmod 600 "$LIGHTTPD_PEM"

# Reload lighttpd to apply changes
/usr/sbin/rc-service lighttpd reload
