from bot.database.manager import DatabaseManager
from bot.database.schemas.bot_engagement import BotEngagementCreate
from fastapi import HTTPException


class BotEngagementCRUD:
    def __init__(self):
        self.db = DatabaseManager().get_client()

    def create_bot_engagement(self, engagement_data: BotEngagementCreate):
        try:
            result = (
                self.db.table("BotEngagement").insert(engagement_data.dict()).execute()
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
                status_code=500, detail=f"Failed to create bot engagement: {e}"
            )

    def get_bot_engagement(self, engagement_id: str):
        try:
            result = (
                self.db.table("BotEngagement")
                .select("*")
                .eq("id", engagement_id)
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Bot engagement not found")
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve bot engagement: {e}"
            )

    def get_bot_engagements(self, bot_id: str):
        try:
            result = (
                self.db.table("BotEngagement")
                .select("*")
                .eq("bot_id", bot_id)
                .execute()
            )
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve bot engagements: {e}"
            )

    def update_bot_engagement(
        self, engagement_id: str, engagement_data: BotEngagementCreate
    ):
        try:
            result = (
                self.db.table("BotEngagement")
                .update(engagement_data.dict())
                .eq("id", engagement_id)
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
                status_code=500, detail=f"Failed to update bot engagement: {e}"
            )

    def delete_bot_engagement(self, engagement_id: str):
        try:
            self.db.table("BotEngagement").delete().eq("id", engagement_id).execute()
            return {"message": "Bot engagement deleted"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete bot engagement: {e}"
            )
