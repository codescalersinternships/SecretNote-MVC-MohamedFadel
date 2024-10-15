# Secret Notes Project

Secret Notes is a Django-based web application that allows users to create and share secure, self-destructing notes. The project is containerized using Docker and can be easily deployed using Docker Compose or Kubernetes.

## Features

- Create secure, encrypted notes
- Set expiration time for notes
- View notes using unique URL keys
- User registration and authentication
- Rate limiting to prevent abuse
- Dockerized application for easy deployment

## Prerequisites

- Docker and Docker Compose
- Kubernetes (optional, for k8s deployment)

## Quick Start

1. Clone the repository:

   ```
   git clone https://github.com/codescalersinternships/SecretNote-MVC-MohamedFadel/tree/development
   cd SecretNote-MVC-MohamedFadel
   ```

2. Start the application using Docker Compose:

   ```
   docker-compose up --build
   ```

3. Access the application at `http://localhost:8008`

## Project Structure

```
.
├── docker-compose.yaml
├── Dockerfile
├── manage.py
├── notes/                 # Main application
├── README.md
├── requirements.txt
├── secret-note/           # Helm chart for Kubernetes deployment
├── secret_notes_project/  # Django project settings
├── staticfiles/
└── wait_for_db.sh
```

## Development

To set up the development environment:

1. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Run migrations:

   ```
   python manage.py migrate
   ```

4. Start the development server:
   ```
   python manage.py runserver
   ```

## Testing

The project includes various test files:

- `notes/tests.py`: Unit tests
- `notes/integration_tests.py`: Integration tests
- `notes/e2e_tests.py`: End-to-end tests

To run the tests:

```
python manage.py test
```

## Deployment

### Docker Compose

Use the provided `docker-compose.yaml` file to deploy the application:

```
docker-compose up --build
```

### Kubernetes

A Helm chart is provided in the `secret-note` directory for Kubernetes deployment. To deploy using Helm:

1. Install Helm (if not already installed)
2. From the project root, run:
   ```
   helm install secret-notes ./secret-note
   ```

## Configuration

The main configuration files are:

- `secret_notes_project/settings.py`: Django settings
- `docker-compose.yaml`: Docker Compose configuration
- `secret-note/values.yaml`: Helm chart values for Kubernetes deployment
