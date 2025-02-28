# Unstruct Backend

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Key Components](#key-components)
   - [Core App](#core-app)
   - [Agent Management App](#agent-management-app)
   - [Common App](#common-app)
4. [Setup and Installation](#setup-and-installation)
5. [API Endpoints](#api-endpoints)
6. [Authentication and Authorization](#authentication-and-authorization)
7. [Database Models](#database-models)
8. [AI Integration](#ai-integration)
9. [Contributing](#contributing)
10. [Best Practices](#best-practices)
11. [FAQ](#faq)

## Project Overview

Unstruct Backend is a Django-based REST API that serves as the "Supabase for AI" - an open-source backbone for AI-powered applications. After observing a common pattern across AI startups repeatedly building the same backend components, we created Unstruct to eliminate this redundancy.

The project provides four essential components that every modern AI application needs:
1. **Data Connectors**: Pull data from various sources (files, cloud buckets, APIs)
2. **Vector Database Integration**: Store and retrieve embeddings for semantic search
3. **LLM Integration**: Connect with OpenAI, local open-source models, or other providers
4. **API Interface**: Enable seamless interaction for end-users and client applications

### Why Open Source?

We believe powerful AI infrastructure shouldn't be hidden behind paywalls or locked into proprietary systems. By open-sourcing Unstruct under the MIT license, we aim to:
- Save development teams from reinventing the same backend pipeline
- Build a vibrant community that improves the infrastructure together
- Enable flexible customization for unique AI workflows
- Provide a foundation built on proven technologies (Django/PostgreSQL)

### Core Features

| Feature | Description |
|---------|-------------|
| Data Connectors | Upload files now, with connectors for S3, Google Drive, etc. on the way |
| Vector & DB Support | Integrate with vector DBs or store data in PostgreSQL for flexible semantic search |
| LLM Model Integration | OpenAI built-in, easily extended for other models (image, audio, custom ML) |
| Action Definition | Define tasks to extract, analyze, or transform data using your chosen AI models |
| API Access | RESTful endpoints so your front-end apps can interact seamlessly with processed data |
| Open Source (MIT) | Fork it, tailor it, and share improvements with the community—no license hassles |

The main purpose of this backend is to:
1. Provide a complete AI backend infrastructure that eliminates repetitive plumbing
2. Enable seamless integration with various data sources and AI models
3. Offer a robust API for building user-facing AI applications
4. Foster an open-source community around AI infrastructure

## System Architecture

The Unstruct Backend is built using Django and Django Rest Framework, following a modular approach with multiple apps:

- `core`: Handles the main business logic and models
- `agent_management`: Manages AI agent configurations and services
- `common`: Provides shared utilities and base models

The project uses a PostgreSQL database for data persistence and integrates with external AI services for document processing.

## Key Components

### Core App

The `core` app is the heart of the Unstruct Backend, containing the main models and business logic:

- `Project`: Represents a collection of tasks and assets
- `Task`: Represents a specific job to be performed on assets
- `Asset`: Represents a document or file to be processed
- `Action`: Defines the types of actions that can be performed on assets

Key files:
- `apps/core/models/`: Contains the main data models
- `apps/core/views/`: Contains the API views for CRUD operations
- `apps/core/serializers/`: Defines how models are serialized for API responses

### Agent Management App

The `agent_management` app handles the integration with AI services and manages AI model configurations:

- `ModelConfiguration`: Stores settings for different AI models
- `BaseAgentService`: Abstract base class for AI agent services
- `OpenAIDataService`: Concrete implementation for OpenAI integration

Key files:
- `apps/agent_management/models/model_configuration.py`: Defines the AI model configuration
- `apps/agent_management/services/base_agent_service.py`: Abstract base class for AI services
- `apps/agent_management/services/open_ai_data_service.py`: OpenAI integration

### Common App

The `common` app provides shared functionality across the project:

- `NBaseModel`: Base model with common fields like created_at, updated_at
- `NBaseSerializer`: Base serializer for consistent API responses
- `NBaselViewSet`: Base viewset with common CRUD operations

Key files:
- `apps/common/models/base_model.py`: Defines the base model classes
- `apps/common/serializers/base_serializer.py`: Defines the base serializer
- `apps/common/views/base_view.py`: Defines the base viewset

## Setup and Installation

### Quick Start (Recommended)

The easiest way to set up and run the project locally is using our setup script:

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd unstruct
   ```

2. Run the local setup script:
   ```bash
   ./scripts/run_local.sh
   ```

The script will automatically:
- Check for required dependencies (Python 3.11, PostgreSQL)
- Create and activate a virtual environment
- Install project dependencies
- Set up environment variables
- Create and configure the database
- Run migrations
- Start the development server

### Manual Setup

If you prefer to set up manually or the script doesn't work for your environment:

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd unstruct
   ```

2. Create and activate a virtual environment:
   ```bash
   python3.11 -m venv unstruct
   source unstruct/bin/activate  # On Windows, use `unstruct\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip3.11 install -r requirements.txt
   ```

4. Set up the environment variables:
   - Copy `.env.sample` to `.env`
   - Fill in the required variables in `.env`

5. Set up PostgreSQL database:
   - Create a database named 'unstruct_local'
   - Configure database settings in `.env`

6. Run migrations:
   ```bash
   python3.11 manage.py migrate
   ```

7. Start the development server:
   ```bash
   python3.11 manage.py runserver
   ```

Note: This project requires Python 3.11 and PostgreSQL. Make sure you have them installed before proceeding with either setup method.

## API Endpoints

The main API endpoints are:

- `/core/projects/`: CRUD operations for projects
- `/core/tasks/`: CRUD operations for tasks
- `/core/assets/`: CRUD operations for assets
- `/core/actions/`: CRUD operations for actions
- `/agent_management/model_configuration/`: CRUD operations for AI model configurations

For detailed API documentation, refer to the Django Rest Framework browsable API interface available at the root URL when running the development server.

## Authentication and Authorization

The project uses Django's built-in authentication system along with Django Rest Framework's token authentication. It also integrates with Amazon Cognito for social authentication.

Key files:
- `apps/core/views/auth_views.py`: Contains the `CognitoLoginView` for Cognito integration
- `config/settings/base.py`: Contains authentication-related settings

To authenticate:
1. Obtain a token using the `/dj-rest-auth/login/` endpoint
2. Include the token in the `Authorization` header of subsequent requests:
   ```
   Authorization: Token <your_token_here>
   ```

## Database Models

The main models in the system are:

1. `User`: Extends Django's AbstractUser model
2. `Project`: Represents a collection of tasks and assets
3. `Task`: Represents a specific job to be performed
4. `Asset`: Represents a document or file to be processed
5. `Action`: Defines types of actions that can be performed
6. `ModelConfiguration`: Stores AI model configurations

All models inherit from `NBaseModel` or `NBaseWithOwnerModel`, which provide common fields like `created_at`, `updated_at`, and `owner`.

## AI Integration

The AI integration is handled primarily through the `agent_management` app:

1. `BaseAgentService`: Defines the interface for AI services
2. `OpenAIDataService`: Implements the OpenAI integration

To use the AI service:
```
python
from apps.agent_management.services.open_ai_data_service import OpenAIDataService
service = OpenAIDataService(openai_api_key="your_api_key")
result = service.extract_response_from_task(task)

```

## Contributing

We welcome contributions to Unstruct! Whether you're fixing bugs, adding new features, or improving documentation, your help is appreciated.

### Quick Start for Contributors

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone <your-fork-url>
   cd unstruct
   ```
3. Set up development environment:
   ```bash
   ./scripts/run_local.sh
   ```
4. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. Make your changes and commit them using [Conventional Commits](https://www.conventionalcommits.org/)
6. Push to your fork and submit a pull request

For detailed guidelines, please see our [Contributing Guide](CONTRIBUTING.md).

### Community
- Join our [Discord Community](https://discord.gg/GKZMkF7fua) for discussions
- Star the repository to show your support!

## Best Practices

1. Always use environment variables for sensitive information (e.g., API keys, database credentials).
2. Follow the DRY (Don't Repeat Yourself) principle by using base classes like `NBaseModel` and `NBaselViewSet`.
3. Use Django's built-in features for security, such as CSRF protection and password hashing.
4. Write unit tests for critical functionality, especially in the `core` app.
5. Use Django's migration system for all database schema changes.
6. Follow PEP 8 style guide for Python code. The project uses tools like Black and isort to maintain consistency.

## FAQ

Q: How do I add a new API endpoint?
A: Create a new view in the appropriate app's `views.py` file, then add the URL to the app's `urls.py` file.

Q: How do I integrate a new AI service?
A: Create a new class that inherits from `BaseAgentService` in the `agent_management` app, implementing the required methods.

Q: How do I handle file uploads for assets?
A: Use the `create_assets_for_project` method in `AssetViewSet`, which handles file uploads and creates Asset objects.

Q: How can I customize the user model?
A: The project uses a custom User model defined in `apps/core/models/user.py`. Extend this model as needed.

Q: How do I run tests?
A: Use the command `python manage.py test` to run all tests. You can specify an app name to run tests for a specific app.

Q: How do I deploy the project?
A: The project includes a Dockerfile and docker-compose.yml for containerization. For production, consider using a platform like AWS Elastic Beanstalk or Heroku.

## Commit Message Guidelines

We follow the Conventional Commits specification for commit messages. This leads to more readable messages that are easy to follow when looking through the project history.

### Commit Message Format
Each commit message consists of a **header**, a **body** and a **footer**. The header has a special format that includes a **type**, a **scope** and a **subject**:

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

### Examples:

1. Feature commit:
```
feat(projects): add file upload capability to project creation

Implemented S3 file upload integration in project creation flow.
Added progress tracking and error handling.

Closes #123
```

2. Bug fix:
```
fix(auth): resolve token refresh issue in API calls

Updated authentication flow to properly handle token refresh.
Added error handling for expired tokens.

Fixes #456
```

3. Documentation:
```
docs(readme): update deployment instructions

Added detailed AWS configuration steps
Updated environment variables section
```

### Types
- `feat`: New feature (referenced in ```typescript:app/components/home/HowItWorks.tsx
startLine: 1
endLine: 18```)
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Changes that don't affect code meaning
- `refactor`: Code changes that neither fix a bug nor add a feature
- `perf`: Performance improvements
- `test`: Adding or modifying tests
- `chore`: Changes to build process or auxiliary tools
- `revert`: Reverts a previous commit

### Scope
The scope should be the name of the module affected (projects, auth, tasks, etc.)

### Subject
The subject contains a succinct description of the change:
- use the imperative, present tense: "change" not "changed" nor "changes"
- don't capitalize the first letter
- no dot (.) at the end

### Body
The body should include the motivation for the change and contrast this with previous behavior.

### Footer
The footer should contain any information about Breaking Changes and is also the place to reference GitHub issues that this commit closes.
