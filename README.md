# nara-backend
Nara Backend is a Django-based web application that serves as the backend for the Nara project. This README provides an overview of the project structure, key components, and setup instructions.

## Project Overview

Nara Backend is built using Django, a high-level Python web framework. The project follows Django's best practices and conventions, including the use of apps for modular structure and the Model-View-Template (MVT) pattern.

### Key Features

- **Asset Management**: Manages various types of assets (documents, files) associated with projects and provides an extraction interface to extract texts from various sources.

## Project Structure

The project is organized into several Django apps, each responsible for specific functionality:

- `agent_management`: Handles AI agent-related operations.
- `core`: Contains core models essential for the application like `Asset`, `Project`, etc.
- `common`: Contains common models and functionalities shared across the project.

### Key Components

1. **Models**:
   - `Asset`: Represents various file types (PDF, DOC, TXT) associated with projects.
   - `Project`: Manages project-related data.
   - `Task`: Represents a task that can be performed on an asset.
   - `Action`: Represents an action that can be performed on an asset.

2. **Services**:
   - `BaseAgentService`: Abstract base class for AI agent services.
   - `BaseVectorStore`: Abstract base class for vector storage implementations.

## Setup and Installation

1. Clone the repository:
   ```
   git clone git@github.com:getnara/nara-backend.git
   cd nara-backend
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create migrations and run the server:
   ```
   make sure you are in nara_backend directory of the repo
   chmod +x ./scripts/run_server.sh
   ./scripts/run_server.sh
   ```


## Development Guidelines

- Follow PEP 8 and Django coding style guidelines.
- Use Django's ORM for database operations.
- Implement proper error handling and validation.
- Write unit tests for new features and bug fixes.
- Use Django's built-in security features and best practices.

## Contributing

Please read the CONTRIBUTING.md file for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE.md file for details.
