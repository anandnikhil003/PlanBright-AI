from personalization.database.manager import SupabaseConnectionManager
from personalization.database.schemas.ai_generated import AIGeneratedOutputCreate
from fastapi import HTTPException


class AIGeneratedOutputCRUD:
    def __init__(self, schema: str):
        self.db = SupabaseConnectionManager(schema=schema).get_client()

    def create_output(self, output_data: AIGeneratedOutputCreate):
        try:
            result = (
                self.db.table("ai_generated_outputs")
                .insert(output_data.dict())
                .execute()
            )
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to create output: No data returned"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create output: {e}")

    def get_output(self, output_id: str):
        try:
            result = (
                self.db.table("ai_generated_outputs")
                .select("*")
                .eq("id", output_id)
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Output not found")
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve output: {e}"
            )

    def update_output(self, output_id: str, output_data: AIGeneratedOutputCreate):
        try:
            result = (
                self.db.table("ai_generated_outputs")
                .update(output_data.dict())
                .eq("id", output_id)
                .execute()
            )
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to update output: No data returned"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update output: {e}")

    def delete_output(self, output_id: str):
        try:
            self.db.table("ai_generated_outputs").delete().eq("id", output_id).execute()
            return {"message": "Output deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete output: {e}")
