from personalization.database.manager import SupabaseConnectionManager
from personalization.database.schemas.teacher import TeacherCreate, Teacher
from fastapi import HTTPException


class TeacherCRUD:
    def __init__(self, schema: str):
        self.db = SupabaseConnectionManager(schema=schema).get_client()

    def create_teacher(self, teacher_data: TeacherCreate):
        try:
            result = self.db.table("teachers").insert(teacher_data.dict()).execute()

            # Assuming result.data contains a list, extract the first item
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create teacher information: No data returned",
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create teacher: {e}"
            )

    def get_teacher(self, teacher_id: int):
        try:
            result = (
                self.db.table("teachers")
                .select("*")
                .eq("id", teacher_id)
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Teacher not found")
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve teacher: {e}"
            )

    def update_teacher(self, teacher_id: int, teacher_data: TeacherCreate):
        try:
            result = (
                self.db.table("teachers")
                .update(teacher_data.dict())
                .eq("id", teacher_id)
                .execute()
            )
            # Assuming result.data contains a list, extract the first item
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update teacher information: No data returned",
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to update teacher: {e}"
            )

    def delete_teacher(self, teacher_id: int):
        try:
            self.db.table("teachers").delete().eq("id", teacher_id).execute()
            return {"message": "Teacher deleted"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete teacher: {e}"
            )
