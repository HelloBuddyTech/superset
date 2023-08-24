#!/usr/bin/env bash

# This procedure is based on
# https://superset.apache.org/docs/installation/installing-superset-using-docker-compose/

# nginx
sudo apt-get install -y nginx
sudo cp ./analytics.hellobuddy.tech-nginx /etc/nginx/sites-available/analytics.hellobuddy.tech
sudo ln -s /etc/nginx/sites-available/analytics.hellobuddy.tech /etc/nginx/sites-enabled/analytics.hellobuddy.tech
sudo systemctl reload nginx
# From https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d analytics.hellobuddy.tech

# Back to superset/
cd ..

# Docker image
docker build -t hellobuddy-superset .

echo ">>>>> ERRORS EXPECTED <<<<<"
echo "ERRORS ARE EXPECTED BELOW! Superset images pull fails: this is normal, because they are available locally"
docker-compose -f docker-compose-non-dev.yml pull
echo "ERRORS ARE EXPECTED ABOVE! Superset images pull fails: this is normal, because they are available locally"

docker-compose -f docker-compose-non-dev.yml --env-file .superset_env up -d
