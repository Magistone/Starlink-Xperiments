#!/bin/bash

#Get grpc file
wget https://raw.githubusercontent.com/sparky8512/starlink-grpc-tools/main/starlink_grpc.py -O ./modules/grpc.py

#generate SSH key

#Install orchestrator
pip install ansible

#Create image for workers
docker build -f Dockerfile -t starlinktool --network=host  .
docker save -o image.tar starlinktool