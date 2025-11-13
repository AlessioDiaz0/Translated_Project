from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn

from models import (
    TranslationPair, 
    PromptRequest, 
    PromptResponse,
    StammeringRequest,
    StammeringResponse,
    StatusResponse
)
from services.translation_service import get_translation_service
from services.stammering_service import detect_stammering
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting RAG Translation Backend...")
    
    # Initialize services (will create database connections)
    try:
        translation_service = get_translation_service()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    logger.info("Shutting down RAG Translation Backend...")


# Create FastAPI app
app = FastAPI(
    title="RAG Translation Backend",
    description="Retrieval-Augmented Generation backend for translation prompts",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/pairs", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def add_translation_pair(pair: TranslationPair):
    "Add a new translation pair to the database"
    try:
        translation_service = get_translation_service()
        translation_service.add_translation_pair(
            source_language=pair.source_language,
            target_language=pair.target_language,
            sentence=pair.sentence,
            translation=pair.translation
        )
        return StatusResponse(status="ok")
    
    except Exception as e:
        logger.error(f"Error adding translation pair: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add translation pair: {str(e)}"
        )


@app.get("/prompt", response_model=PromptResponse)
async def get_translation_prompt(
    source_language: str,
    target_language: str,
    query_sentence: str
):
    "Generate a translation prompt with similar examples from RAG"
    try:
        # Validate request
        request = PromptRequest(
            source_language=source_language,
            target_language=target_language,
            query_sentence=query_sentence
        )
        
        translation_service = get_translation_service()
        prompt = translation_service.generate_translation_prompt(
            source_language=request.source_language,
            target_language=request.target_language,
            query_sentence=request.query_sentence
        )
        
        return PromptResponse(prompt=prompt)
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate translation prompt: {str(e)}"
        )


@app.get("/stammering", response_model=StammeringResponse)
async def detect_stammering_endpoint(
    source_sentence: str,
    translated_sentence: str
):
    "Detect stammering (non-natural repetitions) in a translation"
    try:
        # Validate request
        request = StammeringRequest(
            source_sentence=source_sentence,
            translated_sentence=translated_sentence
        )
        
        has_stammer = detect_stammering(
            source_sentence=request.source_sentence,
            translated_sentence=request.translated_sentence
        )
        
        return StammeringResponse(has_stammer=has_stammer)
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error detecting stammering: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect stammering: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=False
    )
