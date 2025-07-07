# PinHub API

## About

PinHub's backend services, deployed and running on AWS Lambda. This FastAPI-based application provides RESTful APIs for the PinHub platform, handling user management, pin operations, and authentication services.

## A list of all AWS tools used

- Amazon API Gateway
- Amazon CloudFront
- Amazon CloudWatch
- Amazon DynamoDB
- Amazon Q
- Amazon S3
- Amazon SES
- Amazon Transcribe
- AWS ACM
- AWS Amplify
- AWS for GitHub Actions
- AWS Lambda

### Lambda Function Setup

The project uses Mangum as an ASGI adapter to convert the FastAPI application into a Lambda-compatible handler.

### API Gateway Integration

The Lambda function is integrated with AWS API Gateway to handle HTTP requests. The API Gateway:

- Routes incoming requests to the Lambda function
- Manages custom domain configuration with AWS Certificate Manager (ACM) for SSL/TLS certificates
- Handles CORS policies and request/response transformations
- Provides a RESTful interface for the frontend application

### Database Architecture

- **PostgreSQL** serves as the primary relational database for user data, pins, and core business entities
- **DynamoDB** stores security-sensitive and time-critical data, including session tokens and temporary authentication data

### Email Service Integration

- Amazon SES
- Postmark

### Authentication & Security

JWT tokens are generated within the Lambda function and stored in DynamoDB for session management.

## Local Development

### Prerequisites

- Python 3.11+
- uv package manager

### Running the Application

Start the development server:

```bash
uv run uvicorn app.main:app --reload
```

### Code Quality

Run linting and formatting checks:

```bash
uv run ruff check
```

### Update

```bash
uv sync --upgrade
```

## Links

- 🌐 **Website**: [pinhub.xyz](https://pinhub.xyz)
- 💻 **Frontend Repository**: [pinhub-web](https://github.com/chris1ding1/pinhub-web)

## License

[MIT](https://opensource.org/licenses/MIT)

Copyright (c) 2025, [Chris](https://chrisding.xyz)
