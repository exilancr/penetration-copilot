#!/bin/bash

set -e
set -x

# This script is used to start the frontend in development mode.

# Install dependencies
yarn install

# Run the frontend
yarn dev
