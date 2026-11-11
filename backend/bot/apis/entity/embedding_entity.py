from fastapi import APIRouter, Depends
from bot.database.schemas.embedding import EmbeddingCreate, Embedding
from bot.database.crud.embedding import EmbeddingCRUD

bots_embeddings = APIRouter(prefix="/api/bots_embeddings", tags=["Bots_Embeddings"])


def get_embedding_crud():
    return EmbeddingCRUD()


@bots_embeddings.post("/embeddings", response_model=Embedding)
async def create_embedding(
    embedding: EmbeddingCreate,
    embedding_crud: EmbeddingCRUD = Depends(get_embedding_crud),
):
    return embedding_crud.create_embedding(embedding)


@bots_embeddings.get("/embeddings/{embedding_id}", response_model=Embedding)
async def read_embedding(
    embedding_id: str, embedding_crud: EmbeddingCRUD = Depends(get_embedding_crud)
):
    return embedding_crud.get_embedding(embedding_id)


@bots_embeddings.get(
    "/embeddings/content/{content_id}/{content_type}", response_model=list[Embedding]
)
async def list_embeddings_by_content(
    content_id: str,
    content_type: str,
    embedding_crud: EmbeddingCRUD = Depends(get_embedding_crud),
):
    return embedding_crud.get_embeddings_by_content(content_id, content_type)


@bots_embeddings.put("/embeddings/{embedding_id}", response_model=Embedding)
async def update_embedding(
    embedding_id: str,
    embedding: EmbeddingCreate,
    embedding_crud: EmbeddingCRUD = Depends(get_embedding_crud),
):
    return embedding_crud.update_embedding(embedding_id, embedding)


@bots_embeddings.delete("/embeddings/{embedding_id}")
async def delete_embedding(
    embedding_id: str, embedding_crud: EmbeddingCRUD = Depends(get_embedding_crud)
):
    return embedding_crud.delete_embedding(embedding_id)
