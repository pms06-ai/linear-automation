# Copilot Instructions for Linear Automation

## Project Overview

This repository contains Google Cloud Functions that automate interactions with Linear, a project management tool. The primary functions include:

- **Daily Journal**: Creates daily trading journal issues in Linear (runs Mon-Fri at 9:30 AM ET)
- **BigQuery Monitor**: Monitors BigQuery jobs and creates Linear issues for failures (runs every 15 minutes)

## Tech Stack

- **Language**: Python 3.11
- **Platform**: Google Cloud Functions (Gen2)
- **APIs**: Linear GraphQL API, Google Cloud BigQuery
- **CI/CD**: GitHub Actions deploys to GCP on push to `main`
- **Scheduler**: Google Cloud Scheduler triggers functions

## Project Structure

```
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment workflow
├── functions/
│   └── daily-journal/
│       ├── main.py             # Cloud Function entry point
│       └── requirements.txt    # Python dependencies
```

Note: Additional functions (e.g., `bq-monitor/`) may be added in the `functions/` directory following the same structure.

## Coding Standards

### Python

- Use type hints for function parameters and return values
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Include docstrings for all functions
- Handle errors gracefully with appropriate HTTP status codes

### Cloud Functions

- Entry point functions should accept a `request` parameter
- Return tuple of (response_body, status_code)
- Use environment variables for configuration (never hardcode secrets)
- Keep functions focused on a single responsibility

## Dependencies

When adding new dependencies:

- Add them to the relevant `requirements.txt` file
- Pin specific versions (e.g., `requests==2.31.0`)
- Use only well-maintained packages

## Environment Variables

The following environment variables are used (configured via GitHub Secrets):

- `LINEAR_API_KEY`: API key for Linear authentication
- `GCP_PROJECT_ID`: Google Cloud project ID (for BigQuery monitor)
- `GCP_SA_KEY`: Google Cloud service account key (used in deployment)

## Security Guidelines

- Never commit API keys, secrets, or credentials to the repository
- Do not modify workflow files that handle secrets without explicit approval
- Use environment variables for all sensitive configuration
- Do not add `--allow-unauthenticated` to new functions without review

## Testing

- Test Cloud Functions locally using the `functions-framework` package
- Verify GraphQL queries/mutations work correctly before deploying
- Check that error handling returns appropriate status codes

## Deployment

- Deployment happens automatically on push to `main` branch
- Manual deployment can be triggered via `workflow_dispatch`
- Functions deploy to `us-central1` region

## What Copilot Should Avoid

- Modifying `.github/workflows/deploy.yml` secrets handling
- Changing authentication methods without explicit instruction
- Removing error handling or logging
- Adding new functions without corresponding scheduler configuration
