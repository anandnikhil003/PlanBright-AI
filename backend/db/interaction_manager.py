from typing import Optional
from .remote_storage import SupabaseStorage, get_storage
from fastapi import Depends, HTTPException


class InteractionManager:
    """
    A class to manage all the interactions which are happening
    """

    def __init__(self, remote_storage: SupabaseStorage):
        self.remote_storage = remote_storage

    def get_total_interactions_Ai_Coach(self, user_id: str) -> Optional[int]:
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .select("bot_count")
            .eq("user_id", user_id)
            .execute()
        )
        if response.data == []:
            return {"type": "empty", "value": 0}
        elif response.data[0]["bot_count"] is None:
            return {"type": "None", "value": 0}
        return {"type": "exist", "value": response.data[0]["bot_count"]}

    def get_total_interactions_Lesson_Plan(self, user_id: str) -> Optional[int]:
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .select("lesson_planner_count")
            .eq("user_id", user_id)
            .execute()
        )
        if response.data == []:
            return {"type": "empty", "value": 0}
        elif response.data[0]["lesson_planner_count"] is None:
            return {"type": "None", "value": 0}
        return {"type": "exist", "value": response.data[0]["lesson_planner_count"]}

    def get_total_interaction_Rubrik(self, user_id: str) -> Optional[int]:
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .select("rubrik_count")
            .eq("user_id", user_id)
            .execute()
        )
        if response.data == []:
            return {"type": "empty", "value": 0}
        elif response.data[0]["rubrik_count"] is None:
            return {"type": "None", "value": 0}
        return {"type": "exist", "value": response.data[0]["rubrik_count"]}

    def get_total_interaction_Assesment(self, user_id: str) -> Optional[int]:
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .select("assessment_count")
            .eq("user_id", user_id)
            .execute()
        )
        if response.data == []:
            return {"type": "empty", "value": 0}
        elif response.data[0]["assessment_count"] is None:
            return {"type": "None", "value": 0}
        return {"type": "exist", "value": response.data[0]["assessment_count"]}

    def get_total_interaction_Differentiator(self, user_id: str) -> Optional[int]:
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .select("diffrentiation_count")
            .eq("user_id", user_id)
            .execute()
        )
        if response.data == []:
            return {"type": "empty", "value": 0}
        elif response.data[0]["diffrentiation_count"] is None:
            return {"type": "None", "value": 0}
        return {"type": "exist", "value": response.data[0]["diffrentiation_count"]}

    def get_total_interaction_IEP(self, user_id: str) -> Optional[int]:
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .select("IEP_count")
            .eq("user_id", user_id)
            .execute()
        )
        if response.data == []:
            return {"type": "empty", "value": 0}
        elif response.data[0]["IEP_count"] is None:
            return {"type": "None", "value": 0}
        return {"type": "exist", "value": response.data[0]["IEP_count"]}

    def get_total_interaction_UnitPlanner(self, user_id: str) -> Optional[int]:
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .select("unit_count")
            .eq("user_id", user_id)
            .execute()
        )
        if response.data == []:
            return {"type": "empty", "value": 0}
        elif response.data[0]["unit_count"] is None:
            return {"type": "None", "value": 0}
        return {"type": "exist", "value": response.data[0]["unit_count"]}

    def get_total_interaction_feedback(self, user_id: str) -> Optional[int]:
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .select("feedback_count")
            .eq("user_id", user_id)
            .execute()
        )
        if response.data == []:
            return {"type": "empty", "value": 0}
        elif response.data[0]["feedback_count"] is None:
            return {"type": "None", "value": 0}
        return {"type": "exist", "value": response.data[0]["feedback_count"]}

    def calculate_total_interactions(self, user_id: str) -> Optional[int]:
        counts = {
            "bot_count": self.get_total_interactions_Ai_Coach(user_id)["value"],
            "lesson_planner_count": self.get_total_interactions_Lesson_Plan(user_id)[
                "value"
            ],
            "rubrik_count": self.get_total_interaction_Rubrik(user_id)["value"],
            "assessment_count": self.get_total_interaction_Assesment(user_id)["value"],
            "differentiation_count": self.get_total_interaction_Differentiator(user_id)[
                "value"
            ],
            "IEP_count": self.get_total_interaction_IEP(user_id)["value"],
            "feedback_count": self.get_total_interaction_feedback(user_id)["value"],
        }

        total_interaction = sum(count for count in counts.values() if count is not None)
        return total_interaction

    def add_interaction_Ai_Coach(self, user_id: str):
        count = self.get_total_interactions_Ai_Coach(user_id)
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .update({"bot_count": count["value"] + 1})
            .eq("user_id", user_id)
            .execute()
        )

        if response.data == []:
            self.remote_storage.db.table("uc_apps_interaction").insert(
                {"user_id": user_id, "bot_count": count["value"] + 1}
            ).execute()

    def add_interaction_Lesson_Plan(self, user_id: str):
        count = self.get_total_interactions_Lesson_Plan(user_id)
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .update({"lesson_planner_count": count["value"] + 1})
            .eq("user_id", user_id)
            .execute()
        )

        if response.data == []:
            self.remote_storage.db.table("uc_apps_interaction").insert(
                {"user_id": user_id, "lesson_planner_count": count["value"] + 1}
            ).execute()

    def add_interaction_Rubrik(self, user_id: str):
        count = self.get_total_interaction_Rubrik(user_id)
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .update({"rubrik_count": count["value"] + 1})
            .eq("user_id", user_id)
            .execute()
        )

        if response.data == []:
            self.remote_storage.db.table("uc_apps_interaction").insert(
                {"user_id": user_id, "rubrik_count": count["value"] + 1}
            ).execute()

    def add_interaction_Assesment(self, user_id: str):
        count = self.get_total_interaction_Assesment(user_id)
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .update({"assessment_count": count["value"] + 1})
            .eq("user_id", user_id)
            .execute()
        )

        if response.data == []:
            self.remote_storage.db.table("uc_apps_interaction").insert(
                {"user_id": user_id, "assessment_count": count["value"] + 1}
            ).execute()

    def add_interaction_Differentiator(self, user_id: str):
        count = self.get_total_interaction_Differentiator(user_id)
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .update({"diffrentiation_count": count["value"] + 1})
            .eq("user_id", user_id)
            .execute()
        )

        if response.data == []:
            self.remote_storage.db.table("uc_apps_interaction").insert(
                {"user_id": user_id, "diffrentiation_count": count["value"] + 1}
            ).execute()

    def add_interaction_IEP(self, user_id: str):
        count = self.get_total_interaction_IEP(user_id)
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .update({"IEP_count": count["value"] + 1})
            .eq("user_id", user_id)
            .execute()
        )

        if response.data == []:
            self.remote_storage.db.table("uc_apps_interaction").insert(
                {"user_id": user_id, "IEP_count": count["value"] + 1}
            ).execute()

    def add_interaction_Unit(self, user_id: str):
        count = self.get_total_interaction_UnitPlanner(user_id)
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .update({"unit_count": count["value"] + 1})
            .eq("user_id", user_id)
            .execute()
        )

        if response.data == []:
            self.remote_storage.db.table("uc_apps_interaction").insert(
                {"user_id": user_id, "unit_count": count["value"] + 1}
            ).execute()

    def add_interaction_feedback(self, user_id: str):
        count = self.get_total_interaction_feedback(user_id)
        response = (
            self.remote_storage.db.table("uc_apps_interaction")
            .update({"feedback_count": count["value"] + 1})
            .eq("user_id", user_id)
            .execute()
        )

        if response.data == []:
            self.remote_storage.db.table("uc_apps_interaction").insert(
                {"user_id": user_id, "feedback_count": count["value"] + 1}
            ).execute()

    # Function to check database connection
    async def check_db_connection(self) -> bool:
        try:
            response = (
                self.remote_storage.db.table("uc_apps_interaction")
                .select("*")
                .limit(1)
                .execute()
            )
            if response.data:
                return True
            else:
                return False
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database connection failed: {e}"
            )


def get_interaction_manager(
    storage: SupabaseStorage = Depends(get_storage),
) -> InteractionManager:
    if not hasattr(get_interaction_manager, "instance"):
        get_interaction_manager.instance = InteractionManager(remote_storage=storage)
    return get_interaction_manager.instance
