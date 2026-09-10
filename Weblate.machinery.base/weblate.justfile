# justfile — local Weblate + LibreTranslate deployment (Debian, uv)
# https://github.com/necrose99/Myaamia/tree/master/Weblate.machinery.base
# https://docs.weblate.org/en/latest/admin/install/venv-debian.html
#
# Intended for LOCAL MACHINE / LAN, automated research deployment only.
# NOT production-hardened. CHANGE the default admin password (changeme@)
# immediately after `just createadmin`.

set shell := ["bash", "-euo", "pipefail", "-c"]

venv_dir      := env_var_or_default("WEBLATE_VENV", env_var("HOME") + "/weblate-env")
admin_email   := env_var_or_default("WEBLATE_ADMIN_EMAIL", "changeme@")
algic_codes_url := "https://github.com/necrose99/Myaamia/blob/master/scripts/algic_codes.txt"

default:
    just --list

# 1. System build deps (docs.weblate.org venv-debian install guide)
apt-deps:
    sudo apt update
    sudo apt install -y \
        libxml2-dev libxslt-dev libfreetype6-dev libjpeg-dev libz-dev libyaml-dev \
        libffi-dev libacl1-dev liblz4-dev libzstd-dev libxxhash-dev libssl-dev \
        libpq-dev build-essential python3-gdbm python3-dev git

# 2. Optional deps (LDAP / XML signing) — skip if you don't need them
apt-deps-optional:
    sudo apt install -y libldap2-dev libldap-common libsasl2-dev libxmlsec1-dev

# 3. Serving stack: nginx+uwsgi, valkey cache, postgres, exim4, gettext
apt-deps-server:
    sudo apt install -y nginx uwsgi uwsgi-plugin-python3
    sudo apt install -y valkey-server
    sudo apt install -y postgresql postgresql-contrib
    sudo apt install -y exim4
    sudo apt install -y gettext

# 4. Install uv + create the venv, install weblate into it
install-uv:
    curl -LsSf https://astral.sh/uv/install.sh | sh

venv:
    uv venv {{venv_dir}}
    uv pip install --python {{venv_dir}}/bin/python weblate

# 5. Copy settings_example.py -> settings.py
#    (you still need to hand-edit DB creds + Django SECRET_KEY)
configure:
    #!/usr/bin/env bash
    site_pkgs=$(find {{venv_dir}}/lib -maxdepth 1 -type d -name 'python3.*')
    src="$site_pkgs/site-packages/weblate/settings_example.py"
    dst="$site_pkgs/site-packages/weblate/settings.py"
    [ -f "$dst" ] || cp "$src" "$dst"
    echo "Edit $dst — set DB credentials + Django SECRET_KEY before continuing."

# 6. DB migrate + admin user
migrate:
    {{venv_dir}}/bin/weblate migrate

createadmin:
    {{venv_dir}}/bin/weblate createadmin --update {{admin_email}}
    @echo "!! change the '{{admin_email}}' password now — it is not secure as-is !!"

# 7. Celery worker (beat + queues)
celery:
    {{venv_dir}}/bin/celery --app=weblate.utils worker --beat \
        --queues=celery,notify,memory,translate,backup \
        --prefetch-multiplier=1

# 8. Pull the Algic ISO-code list and patch Weblate/Django's language DB.
#    EXPERIMENTAL / unofficial: Weblate + Django don't natively carry all
#    Algic (Algonquian family) iso codes, so this adds missing codes and
#    languages for research use. May not be stable — could crash on rerun.
fetch-algic-codes:
    wget -O algic_codes.txt "{{algic_codes_url}}"

# NOTE: scripts/add_algic_languages.py is a placeholder — point this at
# whichever python3 hack script actually reads algic_codes.txt and calls
# into Django's language model / Weblate's language management commands.
patch-algic-codes: fetch-algic-codes
    {{venv_dir}}/bin/python scripts/add_algic_languages.py algic_codes.txt

# 9. Restart the Weblate/Django service — adjust to however you actually run it
restart:
    sudo systemctl restart weblate || echo "no weblate.service — restart uwsgi/nginx manually"
