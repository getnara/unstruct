#!/bin/bash

# Exit on error
set -e

# Navigate to the backend directory
cd "$(dirname "$0")/.."

# Create virtual environment if it doesn't exist
if [ ! -d "nara" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv nara
fi

# Fish shell specific activation
if [ -n "$FISH_VERSION" ]; then
    source nara/bin/activate.fish
else
    source nara/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip3.11 install -r requirements.txt

# Set up environment variables if .env doesn't exist
if [ ! -f .env ]; then
    echo "Setting up environment variables..."
    cp .env.sample .env
    echo "Please fill in your .env file with required variables"
fi

# Run migrations
echo "Running migrations..."
python3.11 manage.py migrate

# Start development server
echo "Starting development server..."
python3.11 manage.py runserver 