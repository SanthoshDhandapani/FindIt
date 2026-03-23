from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

from app.config import settings


def get_pinecone_index():
    # TODO: Init Pinecone client, create index if not exists (dim=1536, metric=cosine)
    # Return the index object
    raise NotImplementedError


def get_openai() -> OpenAI:
    # TODO: Return a singleton OpenAI client using settings.openai_api_key
    raise NotImplementedError
