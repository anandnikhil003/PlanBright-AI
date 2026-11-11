from personalization.apis.entities.school import SchoolCRUD
from personalization.apis.entities.teacher import TeacherCRUD
from typing import Optional


class PersonalizationEngine:
    def __init__(self, schema="public"):
        self.school_crud = SchoolCRUD(schema)
        self.teacher_crud = TeacherCRUD(schema)

    async def generate_personalized_prompt(self, school_id: int, teacher_id: Optional[int] = None) -> str:
        # Fetch school data
        school_data = self.school_crud.get_school(school_id)
        if not school_data:
            raise ValueError("School data not found.")

        # Construct school-based personalization
        school_prompt = (
            f"School Name: {school_data['name']}\n"
            f"Location: {school_data.get('location', 'N/A')}\n"
            f"Curriculum: {', '.join(school_data.get('curriculum', []))}\n"
            f"Pedagogy: {', '.join(school_data.get('pedagogy', []))}\n"
            f"Additional Info: {school_data.get('meta', {})}\n"
        )

        # Initialize prompt with school information
        personalized_prompt = f"School Information:\n{school_prompt}\n"

        # If teacher_id is provided, fetch teacher data
        if teacher_id:
            teacher_data = self.teacher_crud.get_teacher(teacher_id)
            if not teacher_data:
                raise ValueError("Teacher data not found.")

            # Construct teacher-based personalization
            teacher_prompt = (
                f"Teacher Name: {teacher_data['name']}\n"
                f"Teaching Style: {teacher_data.get('teaching_style', 'N/A')}\n"
                f"Preferences: {teacher_data.get('preferences', {})}\n"
                f"Additional Info: {teacher_data.get('meta', {})}\n"
            )
            personalized_prompt += f"Teacher Information:\n{teacher_prompt}\n"

        return personalized_prompt
