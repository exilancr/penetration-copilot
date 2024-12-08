#!/bin/bash

set -e
set -x

# This script is used to start the frontend in development mode.

# Install dependencies
npm install

# Run the frontend
npm run dev
