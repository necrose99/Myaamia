FROM python:3-alpine
MAINTAINER Niko Schmuck <niko@nava.de> 
##### https://github.com/nikos/python3-alpine-flask-docker/blob/master/Dockerfile
### base template ... 
ARG BUILD_DATE
ARG VCS_REF

FROM python:3-alpine
LABEL maintainer="Niko Schmuck <niko@nava.de>"

# 1. Install System Dependencies (Minimal + Build tools for LDAP/Linguistic tools)
RUN apk add --no-cache \
    tini \
    lighttpd \
    openssl \
    curl \
    unzip \
    build-base \
    openldap-dev \
    python3-dev \
    libffi-dev \
    git	  \
	sqlite-dev \
    build-base \
	zstd \
	 zstd-dev \
	libxml2-dev \
    libxslt-dev \
    gcc \
    musl-dev

# 2. Setup Application Directory
WORKDIR /var/www/Etamology

# 3. Download and Extract the zip from your GitHub repo
RUN curl -L https://github.com/necrose99/Myaamia/raw/master/Etamology-Flask/Etamology-Flask.zip -o Etamology.zip && \
    unzip Etamology.zip && \
    rm Etamology.zip

# 4. Install Requirements (Gunicorn backend + Linguistic + LDAP tools)
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
    lxml


### flask-ldap3-login  flask-ad-auth  

# 5. Configuration Setup
RUN mkdir -p /etc/lighttpd/certs

# 6. Expose Ports (80/443 for Lighttpd Proxy, 5000 for Gunicorn Backend)
EXPOSE 80 443 5000

# 7. Start the Stack using Tini
ENTRYPOINT ["/sbin/tini", "--"]

# CMD starts Lighttpd (foreground) and Gunicorn (foreground via shell)
# Ensure your Lighttpd conf is mapped or copied to /etc/lighttpd/
CMD ["sh", "-c", "lighttpd -f /etc/lighttpd/lighttpd.conf && \
    gunicorn --bind 0.0.0.0:5000 algic_ety_applet_v3:app"]
