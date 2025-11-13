from pydantic import BaseModel, Field, field_validator


class TranslationPair(BaseModel):
    source_language: str = Field(..., min_length=2, max_length=2, description="ISO 639-1 language code")
    target_language: str = Field(..., min_length=2, max_length=2, description="ISO 639-1 language code")
    sentence: str = Field(..., min_length=1, description="Source sentence")
    translation: str = Field(..., min_length=1, description="Target translation")
    
    @field_validator('source_language', 'target_language')
    @classmethod
    def validate_language_code(cls, v: str) -> str:
        if not v.isalpha() or not v.islower():
            raise ValueError("Language code must be 2 lowercase letters")
        return v


class PromptRequest(BaseModel):
    source_language: str = Field(..., min_length=2, max_length=2, description="ISO 639-1 language code")
    target_language: str = Field(..., min_length=2, max_length=2, description="ISO 639-1 language code")
    query_sentence: str = Field(..., min_length=1, description="Sentence to translate")
    
    @field_validator('source_language', 'target_language')
    @classmethod
    def validate_language_code(cls, v: str) -> str:
        if not v.isalpha() or not v.islower():
            raise ValueError("Language code must be 2 lowercase letters")
        return v


class PromptResponse(BaseModel):
    prompt: str


class StammeringRequest(BaseModel):
    source_sentence: str = Field(..., min_length=1)
    translated_sentence: str = Field(..., min_length=1)


class StammeringResponse(BaseModel):
    has_stammer: bool


class StatusResponse(BaseModel):
    status: str = "ok"
