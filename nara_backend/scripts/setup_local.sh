#!/bin/bash

# Create virtual environment
python3.11 -m venv venv

# Fish shell specific activation
if [ -n "$FISH_VERSION" ]; then
    source venv/bin/activate.fish
else
    source venv/bin/activate
fi

# Install dependencies
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.sample .env
    echo "Please fill in your .env file with required variables"
fi

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
