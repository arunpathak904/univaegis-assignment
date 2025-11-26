# UnivAegis — Intelligent Document Verification Platform

UnivAegis is a production-ready document analysis and eligibility system built using Django, React, Docker, and AWS. It enables users to upload academic and financial documents, extract structured data using OCR, and evaluate eligibility based on predefined business rules.

The platform is designed for scalability, secure configuration management, and automated deployment using container orchestration and CI/CD pipelines.

## Features

* Document upload & storage
* OCR-driven content extraction
* Eligibility rules engine
* RESTful API backend
* Containerised frontend & backend
* PostgreSQL database
* CI/CD automated deployment
* Production-ready Nginx server
* Environment-based configuration

## Architecture Overview
	Browser
   	   |
   	   v
	Nginx (Frontend)
   	   |
   	   v
	Django API (Gunicorn)
   	   |
  	   v
	PostgreSQL Database
   	   |
   	   v
	OCR Engine (Tesseract)

## Flow:

1. User uploads a document
2. Backend stores and processes file
3. OCR extracts data
4. Business rules evaluate eligibility
5. Response is returned to the frontend

## Tech Stack
### Backend

* Django + Django REST Framework
* PostgreSQL
* Tesseract OCR
* Gunicorn

### Frontend

* React (Vite)
* Nginx

### Infrastructure

* Docker & Docker Compose
* GitHub Actions
* AWS EC2
* Linux / SSH

## Environment Configuration

All runtime secrets and environment values are stored in a .env file
This file is never committed to version control.

### Required Root .env

Create a .env file in the project root:
```
DB_NAME=your_db_name 
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=db
DB_PORT=5432

DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,EC2_PUBLIC_IP

FRONTEND_API_BASE_URL=http://EC2_PUBLIC_IP:8000/api
```

For local development:
```
FRONTEND_API_BASE_URL=http://localhost:8000/api
DJANGO_DEBUG=True
```

## Project Setup (Docker)
Build & Start
```
docker compose up -d --build
```

Stop
```
docker compose down
```

## Deployment

The application is deployed using a GitHub Actions CI/CD pipeline that:

1. Builds frontend & backend images
2. Pushes images to container registry
3. SSHs into EC2
4. Updates source code
5. Rebuilds containers
6. Runs migrations
7. Collects static files
8. Restarts services

Once configured, deployment is fully automated on push to the main branch.

## Service Access
### Frontend:
```
http://16.176.193.147/
```
API:
```
http://16.176.193.147:8000/api/documents/upload/
http://16.176.193.147:8000/api/eligibility/check/
```

## Frontend Environment Handling

Frontend configuration is injected at Docker build time.
The API base URL is passed from .env and embedded during build.

React always accesses:
```
import.meta.env.VITE_API_BASE_URL
```

This ensures clean separation between environments without code changes.

## Monitoring

View logs:
```
docker compose logs backend
docker compose logs frontend
```

Check containers:
```
docker ps
docker stats
```

## Security Practices
* All application secrets are stored in .env files (never committed)
* Deployment secrets are managed via GitHub Actions Secrets
* SSH-based authentication is used for server access
* No secrets are hardcoded in the codebase
* Environment isolation is maintained between local and production systems
