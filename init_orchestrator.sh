#!/bin/bash

#Get grpc file
wget https://raw.githubusercontent.com/sparky8512/starlink-grpc-tools/main/starlink_grpc.py -O ./modules/grpc.py

#generate SSH key
ssh-keygen -f ~/.ssh/starlinktool -t ed25519 -N ""

#Install orchestrator
sudo apt install -y ansible 

#We need docker locally...
ansible-playbook ./ansible/orchestrator.yml -i localhost, --ask-become-pass

#Create image for workers
sudo docker build -f Dockerfile -t starlinktool --network=host  .
echo -e "\n\nExporting image.."
sudo docker save -o image.tar starlinktool
sudo chmod 644 image.tar