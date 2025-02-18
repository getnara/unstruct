#!/bin/bash

# Exit on error and add error handling
set -e

# Error handling
handle_error() {
    echo "Error: $1"
    exit 1
}
trap 'handle_error "An error occurred on line $LINENO"' ERR

# Navigate to the backend directory
cd "$(dirname "$0")/.." || handle_error "Failed to change directory"

# Check Python version
required_version="3.11"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)" 2>/dev/null; then
    handle_error "Python $required_version or higher is required"
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    handle_error "PostgreSQL is not installed. Please install PostgreSQL first:
    On macOS: brew install postgresql@14
    On Ubuntu: sudo apt-get install postgresql"
fi

# Check if PostgreSQL service is running
if ! pg_isready &> /dev/null; then
    handle_error "PostgreSQL service is not running. Please start it first:
    On macOS: brew services start postgresql@14
    On Ubuntu: sudo service postgresql start"
fi

# Create virtual environment if it doesn't exist
VENV_DIR="unstruct"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv "$VENV_DIR" || handle_error "Failed to create virtual environment"
fi

# Activate virtual environment based on shell
if [ -n "$FISH_VERSION" ]; then
    source "$VENV_DIR/bin/activate.fish" || handle_error "Failed to activate virtual environment"
else
    source "$VENV_DIR/bin/activate" || handle_error "Failed to activate virtual environment"
fi

# Install dependencies
echo "Installing dependencies..."
pip3.11 install -r requirements.txt || handle_error "Failed to install dependencies"

# Set up environment variables if .env doesn't exist
if [ ! -f .env ]; then
    echo "Setting up environment variables..."
    if [ -f .env.sample ]; then
        cp .env.sample .env || handle_error "Failed to copy .env.sample to .env"
    else
        handle_error ".env.sample not found"
    fi
    echo "Please fill in your .env file with required variables"
fi

# Load and validate environment variables
echo "Loading environment variables..."
if [ -f .env ]; then
    # Export variables without empty values and comments
    set -a
    source .env
    set +a
else
    handle_error ".env file not found"
fi

# Validate required environment variables with default values
DB_NAME=${DB_NAME:-unstruct_local}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

echo "Using database configuration:"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"

# Create database user if it doesn't exist (only if we're not using the default postgres user)
if [ "$DB_USER" != "postgres" ]; then
    if ! psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        echo "Creating database user $DB_USER..."
        createuser --createdb "$DB_USER" || handle_error "Failed to create database user"
        psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" || handle_error "Failed to set user password"
    fi
fi

# Create database if it doesn't exist
echo "Checking database..."
if ! psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Creating database $DB_NAME..."
    createdb -U postgres --owner="$DB_USER" "$DB_NAME" || handle_error "Failed to create database"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" || handle_error "Failed to grant privileges"
else
    echo "Database $DB_NAME already exists."
fi

# Test database connection
echo "Testing database connection..."
if ! PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
    handle_error "Failed to connect to database. Please check your credentials."
fi

# Create and run migrations
echo "Checking for model changes..."
python3.11 manage.py makemigrations || handle_error "Failed to create migrations"

echo "Running migrations..."
python3.11 manage.py migrate || handle_error "Failed to run migrations"

# Start development server
echo "Starting development server..."
python3.11 manage.py runserver 