# Kayfa Sales Agent

> A Streamlit application for Kayfa’s sales workflow, combining authenticated AI chat, CRM lead capture, and monitoring dashboards on top of MongoDB, Qdrant, Groq, and a local knowledge base.

## Overview

Kayfa Sales Agent is designed for internal sales and support operations. Users sign in with a role, then access the parts of the app they are authorized to use: chat, CRM, and monitoring. The chat experience uses Kayfa’s markdown and JSON knowledge files, semantic retrieval, and routed model selection to answer questions, capture leads, and log usage for later analysis.

## Features

- Role-based access for `admin`, `sales`, and `user` accounts.
- Bilingual chat experience with Arabic and English rendering support.
- Lead capture flow that stores qualified CRM tickets in MongoDB.
- CRM dashboard with filtering, search, and lead summaries.
- Monitoring dashboard with cost, token, latency, and trace views.
- Semantic cache to reuse similar answers and reduce repeated model calls.
- Model routing between faster and stronger Groq-backed models based on query complexity.
- Local knowledge ingestion from `data/text` and `data/json`.

## Tech Stack

| Layer | Technology |
| --- | --- |
| UI | Streamlit |
| Authentication | bcrypt, MongoDB |
| Agent / Chat | pydantic-ai, Groq |
| Retrieval | Qdrant, sentence-transformers, fastembed |
| Database | MongoDB |
| Data Sources | Markdown files in `data/text` and JSON files in `data/json` |

## Access Model

- `admin`: full access to chat, CRM, and monitoring.
- `user`: chat access.

## Getting Started

- Deployed App: [Streamlit link](https://kayfa-ai-sales-agent.streamlit.app/)

### Prerequisites

- Python 3.10 or newer
- MongoDB instance
- Qdrant instance
- Groq API key

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configuration

The app reads secrets from Streamlit first and falls back to environment variables. Add the required values using either `.streamlit/secrets.toml` or a local `.env` file.

Example `.env`:

```env
MONGODB_URI=your-mongodb-connection-string
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-api-key
GROQ_API_KEY=your-groq-api-key
```

Example `.streamlit/secrets.toml`:

```toml
MONGODB_URI = "your-mongodb-connection-string"
QDRANT_URL = "your-qdrant-url"
QDRANT_API_KEY = "your-qdrant-api-key"
GROQ_API_KEY = "your-groq-api-key"
```

### Run Locally

```bash
streamlit run app/app.py
```

## Project Structure

```text
app/
  app.py            # main app shell and page routing
  auth.py           # login, signup, and role permissions
  chat.py           # AI sales chat UI and response handling
  crm.py            # CRM lead dashboard
  dashboard.py      # monitoring and cost analytics
  optimizations.py  # semantic cache and query routing
data/
  json/        # structured data
  text/        # knowledge-base documents
images/        # Kayfa branding assets
notebooks/
  AI_Sales_Agent.ipynb
```

## Notes

- The app expects the Kayfa branding images in `images/`.
- MongoDB stores users, sessions, messages, CRM tickets, and `usage_logs`.
- Pricing for cost tracking is centralized in `app/app.py` and should be reviewed if provider pricing changes.
- The monitoring dashboard shows per-user, per-conversation, per-message, and optimization views based on stored usage logs.

## License

See [LICENSE](LICENSE) for details.
