#!/bin/bash

#Get grpc file
wget https://raw.githubusercontent.com/sparky8512/starlink-grpc-tools/main/starlink_grpc.py -O ./modules/grpc.py

#generate SSH key
ssh-keygen -f ~/.ssh/starlinktool -t ed25519 -N ""

#Install orchestrator
pip install -r requirements_orchestrator.txt 

#We need docker locally...
ansible-playbook ./ansible/orchestrator.yml -i localhost, --ask-become-pass

#Create image for workers
sudo docker build -f Dockerfile -t starlinktool --network=host  .
echo "Exporting image.."
sudo docker save -o image.tar starlinktool