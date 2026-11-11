from bot.database.manager import DatabaseManager
from bot.database.schemas.embedding import EmbeddingCreate
from fastapi import HTTPException


class EmbeddingCRUD:
    def __init__(self):
        self.db = DatabaseManager().get_client()

    def create_embedding(self, embedding_data: EmbeddingCreate):
        try:
            result = self.db.table("Embeddings").insert(embedding_data.dict()).execute()
            # Assuming result.data contains a list, extract the first item
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to create school: No data returned"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create embedding: {e}"
            )

    def get_embedding(self, embedding_id: str):
        try:
            result = (
                self.db.table("Embeddings")
                .select("*")
                .eq("id", embedding_id)
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Embedding not found")
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve embedding: {e}"
            )

    def get_embeddings_by_content(self, content_id: str, content_type: str):
        try:
            result = (
                self.db.table("Embeddings")
                .select("*")
                .eq("content_id", content_id)
                .eq("content_type", content_type)
                .execute()
            )
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve embeddings: {e}"
            )

    def update_embedding(self, embedding_id: str, embedding_data: EmbeddingCreate):
        try:
            result = (
                self.db.table("Embeddings")
                .update(embedding_data.dict())
                .eq("id", embedding_id)
                .execute()
            )
            # Assuming result.data contains a list, extract the first item
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to create school: No data returned"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to update embedding: {e}"
            )

    def delete_embedding(self, embedding_id: str):
        try:
            self.db.table("Embeddings").delete().eq("id", embedding_id).execute()
            return {"message": "Embedding deleted"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete embedding: {e}"
            )
