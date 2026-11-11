from personalization.database.manager import SupabaseConnectionManager
from personalization.database.schemas.embedding import EmbeddingCreate
from fastapi import HTTPException


class EmbeddingCRUD:
    def __init__(self, schema: str):
        self.db = SupabaseConnectionManager(schema=schema).get_client()

    def create_embedding(self, embedding_data: EmbeddingCreate):
        try:
            result = self.db.table("embeddings").insert(embedding_data.dict()).execute()
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create embedding: No data returned",
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create embedding: {e}"
            )

    def get_embedding(self, embedding_id: str):
        try:
            result = (
                self.db.table("embeddings")
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

    def update_embedding(self, embedding_id: str, embedding_data: EmbeddingCreate):
        try:
            result = (
                self.db.table("embeddings")
                .update(embedding_data.dict())
                .eq("id", embedding_id)
                .execute()
            )
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update embedding: No data returned",
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to update embedding: {e}"
            )

    def delete_embedding(self, embedding_id: str):
        try:
            self.db.table("embeddings").delete().eq("id", embedding_id).execute()
            return {"message": "Embedding deleted"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete embedding: {e}"
            )
