
# HelpMeFind 🔍

## AI-Powered Local Discovery Assistant

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/) [![LangChain](https://img.shields.io/badge/powered%20by-LangChain-green)](https://www.langchain.com/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**HelpMeFind** is an intelligent location-based recommendation system that leverages AI to help you discover the perfect places nearby without the endless scrolling and review-reading.

[Live Demo](https://helpmefind.pratim.me/) _(Note: If unavailable, Google API costs may have exceeded budget)_

----------

## 🌟 The Problem HelpMeFind Solves

While vacationing in Europe, I encountered a common traveler's dilemma: despite having access to countless places in Google Maps, determining which ones were actually worth visiting required tedious scrolling through ratings and reviews. As an engineer, I saw an opportunity to solve this problem with AI.

Instead of manually sifting through dozens of reviews to get the real picture of a venue, **HelpMeFind** uses AI to:

1. Take your current location and search query
2. Find relevant places using Google Places API
3. Collect and analyze reviews
4. Generate an insightful, balanced summary using LLM technology

The result? Make better decisions in seconds, not minutes.

----------

## ✨ Technical Features

- **Location-Aware Search**: Uses the user's current geographic coordinates for accurate local recommendations
- **AI-Powered Agents**: Built with LangChain framework to create intelligent search flows
- **Smart Review Analysis**: Processes and summarizes multiple reviews to extract meaningful insights
- **Multi-Provider LLM Support**: Easily switch between Google Gemini, Groq, and Ollama models

## 🧠 Under the Hood

**HelpMeFind** combines several powerful technologies:

- **LangChain** (🦜️🔗): For building the intelligent agent architecture and chains
- **Google Places API**: For retrieving location data and user reviews
- **Modular Agent System**: Specialized agents in `agents/` directory for targeted tasks
- **Custom Chains**: Reusable reasoning patterns in `chains/` directory
- **Flask Backend**: Lightweight web framework to serve the application
- **Local Caching**: SQLite-based caching system to reduce API calls

----------

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- pipenv
- LLM API access (configured in `llm.py`)
- Google Places API key

### Installation

1. Clone the repository

    ```bash
    git clone https://github.com/pratims091/helpmefind
    cd helpmefind

    ```

2. Install dependencies with pipenv

    ```bash
    pipenv install

    ```

3. Set up environment variables

    ```bash
    cp sample.env .env

    ```

4. Edit your `.env` file with the necessary API keys

    ```
    GOOGLE_PLACES_API_KEY=your_key_here
    GOOGLE_API_KEY=your_key_here
    # Or configure alternative LLMs

    ```

5. Run the application

    ```bash
    pipenv run python app.py

    ```

6. Navigate to the local server address (typically <http://127.0.0.1:5000/>)

### Using Mock Data

Don't have API keys yet? No problem! Use the provided mock data:

```bash
# Set this in your .env file
MOCK_API_REQUESTS=True

```

The mock data is located in the `./mock_data` folder and includes:

- `places.json`: Sample place data for testing
- `places_images.json`: Sample images for the mock places

----------

## 📦 Project Structure

```
helpmefind/
├── agents/                  # AI agent implementations
│   ├── __init__.py
│   └── places_search.py     # Agent for searching places
├── chains/                  # Custom LangChain chains
│   ├── __init__.py
│   └── custom_chains.py     # Specialized reasoning chains
├── tools/                   # Custom tools for agents
│   ├── __init__.py
│   └── search_google_maps.py # Google Maps search integration
├── cache/                   # Local cache storage
│   └── cache.db             # SQLite cache database
├── mock_data/               # Sample data for testing without API
│   ├── places.json
│   └── places_images.json
├── static/                  # Frontend assets
│   ├── scripts/
│   │   ├── footer.js
│   │   └── header.js
│   └── styles/
│       └── main.css
├── templates/               # HTML templates
│   └── index.html
├── app.py                   # Flask application entry point
├── main.py                  # Core application logic
├── llm.py                   # LLM configuration
├── output_parsers.py        # Parsers for LLM outputs
├── Dockerfile               # Container definition
├── Pipfile                  # Dependencies
├── Pipfile.lock             # Locked dependencies
├── sampl.env                # Environment variable template
└── README.md                # Project documentation

```

## 🔄 Customizing the LLM

The application's LLM integration is defined in `llm.py`. The application supports multiple LLM providers which can be easily switched via environment variables:

```python
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
import os

load_dotenv()

def get_llm():
    llm_to_use = os.getenv("LLM_TO_USE", "google")
    model = os.getenv("LLM_MODEL", "gemini-2.0-flash")

    match llm_to_use:
        case "google":
            return ChatGoogleGenerativeAI(model=model, temperature=0)
        case "groq":
            return ChatGroq(model=model, temperature=0)
        case "ollama":
            return ChatOllama(model=model, temperature=0)
        case _:
            raise ValueError(f"Unsupported LLM_TO_USE value: {llm_to_use}")

```

To switch models, simply update your `.env` file:

```
# Use Google's Gemini model (default)
LLM_TO_USE=google
LLM_MODEL=gemini-2.0-flash

# Or use Groq
# LLM_TO_USE=groq
# LLM_MODEL=llama3-70b-8192

# Or use a local model with Ollama
# LLM_TO_USE=ollama
# LLM_MODEL=llama3

```

----------

## 🔧 Key Components

### Places Search Agent (`agents/places_search.py`)

Specialized agent that handles querying and processing location data from Google Places API.

### Custom Chains (`chains/custom_chains.py`)

Pre-configured reasoning patterns that enable consistent processing and summarization of place data.

### Google Maps Search Tool (`tools/search_google_maps.py`)

Custom tool that interfaces with Google Places API to retrieve location information.

### Output Parsers (`output_parsers.py`)

Converts raw LLM outputs into structured data formats for the application.

### Caching System (`cache/`)

Reduces API calls by storing previous queries and responses in a local SQLite database.

----------

## 👨‍💻 Contributing

This is my first deployed AI-powered application, and I welcome contributions from the community! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Improvement

- Enhanced UI/UX (the current frontend was generated with AI assistance)
- Support for additional LLM providers
- More sophisticated review analysis algorithms
- Multi-language support for international travelers
- Mobile app version

----------

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

----------

## 🙏 Acknowledgments

- [LangChain](https://www.langchain.com/) for the incredible agent framework
- [Google Cloud Platform](https://cloud.google.com/) for the Places API
- The open-source AI community for inspiration and resources

----------

_Built with ❤️ by an engineer who was tired of reading too many restaurant reviews_
