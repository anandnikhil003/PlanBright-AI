from personalization.database.manager import SupabaseConnectionManager
from personalization.database.schemas.course_material import CourseMaterialCreate
from fastapi import HTTPException


class CourseMaterialCRUD:
    def __init__(self, schema: str):
        self.db = SupabaseConnectionManager(schema=schema).get_client()

    def create_course_material(self, material_data: CourseMaterialCreate):
        try:
            result = (
                self.db.table("course_materials").insert(material_data.dict()).execute()
            )
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create course material: No data returned",
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create course material: {e}"
            )

    def get_course_material(self, material_id: str):
        try:
            result = (
                self.db.table("course_materials")
                .select("*")
                .eq("id", material_id)
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Course material not found")
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve course material: {e}"
            )

    def update_course_material(
        self, material_id: str, material_data: CourseMaterialCreate
    ):
        try:
            result = (
                self.db.table("course_materials")
                .update(material_data.dict())
                .eq("id", material_id)
                .execute()
            )
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update course material: No data returned",
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to update course material: {e}"
            )

    def delete_course_material(self, material_id: str):
        try:
            self.db.table("course_materials").delete().eq("id", material_id).execute()
            return {"message": "Course material deleted"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete course material: {e}"
            )

    def get_course_for_school(self, school_id: str):
        try:
            response = (
                self.db.table("course_materials")
                .select("*")
                .eq("school_id", school_id)
                .execute()
            )

            if response.data:
                return response.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to fetch course material for the given school_id: {school_id} : No data returned",
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch course material for the given school_id: {e}",
            )
