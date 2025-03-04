# Unstruct: Intelligent Document Data Extraction

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

Unstruct is a powerful open-source data extraction platform that pulls structured information from unstructured documents. Built for developers and data teams, Unstruct eliminates the tedious work of manually extracting data from invoices, reports, and other business documents.

### The Data Extraction Challenge

Organizations struggle with extracting usable data from documents that come in various formats:

* **Inconsistent Layouts**: Every vendor uses different invoice formats
* **Mixed Content Types**: Documents contain text, tables, and images that all need extraction
* **Hidden Relationships**: Critical data points are scattered across multiple pages
* **Format Variations**: Information arrives as PDFs, scanned images, or digital documents

Unstruct solves these challenges by providing a unified extraction pipeline that converts document chaos into clean, structured data.

### Key Extraction Capabilities

#### Field Extraction
* Extract specific data points like invoice numbers, dates, and amounts
* Identify and extract named entities like people, organizations, and locations
* Capture metadata including document type, origin, and processing history

#### Table Extraction
* Convert complex tables into structured data formats
* Maintain header-to-data relationships in multi-level tables
* Handle merged cells, nested tables, and irregular layouts
* Extract tabular data even when formatting is inconsistent

#### Relationship Mapping
* Connect related data points across document sections
* Establish parent-child relationships between extracted entities
* Map line items to their corresponding headers and totals
* Link extracted data to source locations for verification

Unstruct delivers extracted data in clean, structured formats ready for database storage, API transmission, or direct use in applications. Each extraction includes confidence scores and source references for validation.

### Supported Document Types
* Business Documents: Invoices, purchase orders, receipts, contracts
* Forms: Applications, surveys, questionnaires, enrollment forms
* Reports: Financial statements, compliance documents, technical reports
* Identity Documents: IDs, licenses, certificates, credentials

### Why Open Source?

We built Unstruct as open-source because data extraction should be:
- Accessible to organizations of all sizes, not just enterprises with large budgets
- Transparent in how it processes sensitive business documents
- Customizable for specific industry needs and document types
- Community-driven to support the widest range of extraction scenarios

### Core Features

| Feature | Description |
|---------|-------------|
| Targeted Field Extraction | Pull specific data points from documents with high precision |
| Intelligent Table Recognition | Convert complex tables into structured data formats |
| Multi-Format Support | Process PDFs, images, and text documents with a single API |
| Confidence Scoring | Get reliability metrics for each extracted data point |
| Source Referencing | Link extracted data to its original location in the document |
| Extraction Templates | Create reusable templates for common document types |
| Batch Processing | Extract data from multiple documents in parallel |

The main purpose of Unstruct is to:
1. Transform document-trapped data into structured, usable information
2. Eliminate manual data entry and human error in document processing
3. Provide developers with a reliable API for document data extraction
4. Enable automation of document-heavy business processes

## System Architecture

Unstruct is built as a modular data extraction platform with several key components:

- `core`: Contains the extraction engine, document processors, and field extractors
- `agent_management`: Manages AI models that power the extraction capabilities
- `common`: Provides shared utilities and base components

The architecture follows a multi-stage extraction pipeline:

1. **Document Ingestion**: 
   - Upload documents via API or import from storage services
   - Convert documents to normalized formats for processing
   - Apply pre-processing to enhance document quality

2. **Document Analysis**:
   - Identify document type and structure
   - Detect regions of interest (tables, form fields, headers)
   - Create a spatial map of document elements

3. **Data Extraction**:
   - Apply specialized extractors for different data types
   - Extract text fields, tables, and form elements
   - Maintain spatial relationships between extracted elements

4. **Post-Processing**:
   - Calculate confidence scores for each extraction
   - Format data according to schema definitions

5. **Result Delivery**:
   - Store extraction results in structured formats
   - Provide API access to extracted data
   - Generate export files in various formats (JSON, CSV, Excel)

The system uses PostgreSQL for data storage and integrates with AI services to power the extraction capabilities. All components are designed to be horizontally scalable for high-volume document processing.

## Key Components

### Core App

The `core` app contains the main extraction engine and document processing components:

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
