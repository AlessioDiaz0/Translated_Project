# RAG Translation Backend

A FastAPI-based translation service using Retrieval-Augmented Generation (RAG) with ChromaDB vector storage. Provides context-aware translation prompts and detects non-natural repetitions in translations.

## Features

### Translation Prompt Generation
- **Semantic Search**: Retrieves similar translation examples using sentence embeddings
- **Context-Aware**: Generates prompts with up to 4 relevant examples from past translations
- **Language Support**: Handles any language pair using ISO 639-1 codes
- **Vector Storage**: ChromaDB for efficient similarity search
s
### Stammering Detection
- **Pattern Recognition**: Identifies non-natural repetitions in translations
- **Multi-Level Analysis**: Detects both character elongation and phrase repetition
- **Context Sensitive**: Distinguishes between natural and artificial repetitions

### Data Management
- **Persistent Storage**: Vector embeddings stored in ChromaDB
- **Flexible Embedding**: Uses sentence-transformers for semantic understanding
- **REST API**: Clean endpoint design for integration

## API Endpoints

### `POST /pairs`
Store translation pairs for future retrieval.

```json
{
  "source_language": "en",
  "target_language": "it",
  "sentence": "Hello, how are you?",
  "translation": "Ciao, come stai?"
}
```

### `GET /prompt`
Generate translation prompt with similar examples.

**Query Parameters:**
- `source_language`: ISO 639-1 code (e.g., "en")
- `target_language`: ISO 639-1 code (e.g., "it")
- `query_sentence`: Text to translate

**Response:**
```
Translate the following sentence from en to it:

"See you later, my friend."

Here are some similar translation examples:

1. en: "See you later."
   it: "Ci vediamo dopo."

2. en: "See you soon."
   it: "A presto."

3. en: "See you tomorrow."
   it: "Ci vediamo domani."

4. en: "Good evening!"
   it: "Buonasera!"
```

### `GET /stammering`
Detect non-natural repetitions in translations.

**Query Parameters:**
- `source_sentence`: Original text
- `translated_sentence`: Translation to check

**Response:**
```json
{
  "has_stammer": false
}
```

### `GET /health`
Service health check.

## Quick Start

### Using Docker (Recommended)

```bash
# Build and start
docker-compose up -d

# Stop
docker-compose down
```

API available at `http://localhost:8000`

## Configuration

Environment variables:

```env
CHROMA_PERSIST_DIR=./chroma_data
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
PORT=8000
```

## Technical Stack

- **FastAPI**: REST API framework
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Text embedding generation
- **Pydantic**: Request/response validation
- **Docker**: Containerized deployment

## Architecture

```
├── main.py                 # FastAPI application & endpoints
├── models.py              # Pydantic models
├── config.py              # Configuration management
├── services/
│   ├── translation_service.py   # RAG translation logic
│   ├── embedding_service.py     # Text embedding generation
│   └── stammering_service.py    # Repetition detection
└── database/
    └── vector_store.py    # ChromaDB interface
```

## Testing

API documentation available at `http://localhost:8000/docs` (Swagger UI)

## Execution Logs

Full execution logs available in `logs/logs.txt`, obtained running your client.py