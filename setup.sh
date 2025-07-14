#!/bin/bash
# setup.sh
# One-click setup for dev environment
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Optionally, pull docker images
docker-compose pull
# To run in dev mode, see README

