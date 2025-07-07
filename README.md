# PinHub API

🌐 **Website**: [PinHub](https://pinhub.xyz)

## About the use of AWS Lambda

AWS Lambda is utilized as the core backend compute service for PinHub's APIs. It processes requests sent from the frontend through Amazon API Gateway and handles a variety of tasks, including:

- **Sending verification emails**: It uses Amazon SES or Postmark to deliver emails for user verification.
- **Managing user data**: It connects to a PostgreSQL database to query or create user information.
- **Storing tokens and records**: It saves tokens and email sending records in Amazon DynamoDB, a NoSQL database service.
- **Handling bookmark data**: It interacts with the PostgreSQL database to save and manage bookmark data.
- **Storing files**: When creating bookmark data, it uploads audio and image files to Amazon S3, a scalable storage service.
- **Speech to Text**: Amazon Transcribe
- **Log**: Amazon CloudWatch

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

## License

[MIT](https://opensource.org/licenses/MIT)

Copyright (c) 2025, [Chris](https://chrisding.xyz)
