#!/bin/bash

set -e

# This script is used to start the backend in development mode.
# Create venv
python3 -m venv /tmp/venv

# Activate venv
source /tmp/venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
python3 manage.py --host=0.0.0.0
