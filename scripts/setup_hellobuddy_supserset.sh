#!/usr/bin/env bash

# This procedure is based on
# https://superset.apache.org/docs/installation/installing-superset-using-docker-compose/

# From https://docs.docker.com/engine/install/ubuntu/
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-compose
sudo docker run hello-world
sudo systemctl enable docker

# From https://docs.docker.com/engine/install/linux-postinstall/
sudo groupadd docker
sudo usermod -aG docker $USER
docker run hello-world

cd superset
docker build -t hellobuddy-superset .

echo ">>>>> ERRORS EXPECTED <<<<<"
echo "ERRORS ARE EXPECTED BELOW! Superset images pull fails: this is normal, because they are available locally"
docker-compose -f docker-compose-non-dev.yml pull
echo "ERRORS ARE EXPECTED ABOVE! Superset images pull fails: this is normal, because they are available locally"

docker-compose -f docker-compose-non-dev.yml up -d


sudo apt-get install -y nginx
cp ./analytics.hellobuddy.tech-nginx /etc/nginx/sites-available/analytics.hellobuddy.tech
sudo ln -s /etc/nginx/sites-available/analytics.hellobuddy.tech /etc/nginx/sites-enabled/analytics.hellobuddy.tech
sudo systemctl reload nginx
# From https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d analytics.hellobuddy.tech
