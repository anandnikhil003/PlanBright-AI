from personalization.database.manager import SupabaseConnectionManager
from personalization.database.schemas.school import SchoolCreate
from fastapi import HTTPException


class SchoolCRUD:
    def __init__(self, schema: str):
        self.db = SupabaseConnectionManager(schema=schema).get_client()

    async def create_school(self, school_data: SchoolCreate):
        try:
            # Insert the data and get the response
            result = self.db.table("schools").insert(school_data.dict()).execute()

            # Assuming result.data contains a list, extract the first item
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to create school: No data returned"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create school: {e}")

    def get_school(self, school_id: str):
        try:
            result = (
                self.db.table("schools")
                .select("*")
                .eq("id", school_id)
                .single()
                .execute()
            )
            print(result)
            if not result.data:
                raise HTTPException(status_code=404, detail="School not found")
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve school: {e}"
            )

    def update_school(self, school_id: int, school_data: SchoolCreate):
        try:
            result = (
                self.db.table("schools")
                .update(school_data.dict())
                .eq("id", school_id)
                .execute()
            )
            # Assuming result.data contains a list, extract the first item
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to update school: No data returned"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update school: {e}")

    def delete_school(self, school_id: int):
        try:
            self.db.table("schools").delete().eq("id", school_id).execute()
            return {"message": "School deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete school: {e}")
