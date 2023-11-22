#!/bin/sh

# Add Docker's official GPG key
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -y -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo '*****************************************************'
echo '*               Added official GPG key              *'
echo '*****************************************************'

# Add the repository to the Apt sources
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
echo '*****************************************************'
echo '*           Added repository to Apt sources         *'
echo '*****************************************************'

# Install the latest version
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-compose
echo '*****************************************************'
echo '*          Installed the latest version             *'
echo '*****************************************************'

# Create docker group
sudo groupadd docker

# Add current user to the docker group
sudo usermod -aG docker $USER

# Activate group changes and verify installation
echo '*****************************************************'
echo '*           Verifying the installation ...          *'
echo '*****************************************************'
newgrp docker << EOF

docker run --rm hello-world

EOF
