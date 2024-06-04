#!/bin/bash

#Get grpc file
wget https://raw.githubusercontent.com/sparky8512/starlink-grpc-tools/main/starlink_grpc.py -O ./modules/grpc.py

#generate SSH key
ssh-keygen -f ~/.ssh/starlinktool -t ed25519 -N ""

#Install orchestrator
pip install -r requirements_orchestrator.txt 

#Create image for workers
docker build -f Dockerfile -t starlinktool --network=host  .
docker save -o image.tar starlinktool