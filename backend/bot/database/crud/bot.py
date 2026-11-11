from bot.database.manager import DatabaseManager
from bot.database.schemas.bot import BotCreate
from fastapi import HTTPException
from collections import defaultdict
from bot.database.schemas.bot import BotDetails, MyBotDetails
from typing import List
from bot.database.schemas.bot import BotEditData, CreateBotInfo, CreateIframeInfo
import uuid
from datetime import datetime, timedelta, timezone
from bot.apis.utils import CommonUtil
from typing import Optional


class BotCRUD:
    def __init__(self):
        self.db = DatabaseManager().get_client()

    def create_bot(
        self,
        id,
        name,
        description,
        persona,
        purpose,
        icon,
        color_palette,
        gpt_model,
        is_published,
        scope,
        created_by,
        user_id,
        bot_type,
        bot_embedding_id,
    ) -> CreateBotInfo:
        try:
            if id is None:
                id = self.generate_bot_id()
                values = {
                    "id": id,
                    "name": name,
                    "description": description,
                    "persona": persona,
                    "purpose": purpose,
                    "icon": icon,
                    "color_palette": color_palette,
                    "gpt_model": gpt_model,
                    "is_published": is_published,
                    "scope": scope,
                    "created_by": created_by,
                    "user_id": user_id,
                    "bot_type": bot_type,
                    "temp_name": name,
                    "temp_description": description,
                    "temp_persona": persona,
                    "temp_purpose": purpose,
                    "temp_icon": icon,
                    "temp_color_palette": color_palette,
                    "temp_gpt_model": gpt_model,
                    "temp_scope": scope,
                }
                result = self.db.table("Bots").insert(values).execute()
            # Assuming result.data contains a list, extract the first item
            else:
                if bot_type == "temporary":
                    values = {
                        "temp_name": name,
                        "temp_description": description,
                        "temp_persona": persona,
                        "temp_purpose": purpose,
                        "temp_icon": icon,
                        "temp_color_palette": color_palette,
                        "temp_gpt_model": gpt_model,
                        "temp_scope": scope,
                    }
                    result = self.db.table("Bots").update(values).eq("id", id).execute()
                else:
                    values = {
                        "name": name,
                        "description": description,
                        "persona": persona,
                        "purpose": purpose,
                        "icon": icon,
                        "color_palette": color_palette,
                        "gpt_model": gpt_model,
                        "scope": scope,
                    }
                    result = self.db.table("Bots").update(values).eq("id", id).execute()
            if bot_embedding_id:
                self.db.table("BotFiles2").update({"bot_id": id}).eq(
                    "id", bot_embedding_id
                ).execute()
            if result.data:
                return CreateBotInfo(id=id, bot_type=bot_type)
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to create bot: No data returned"
                )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create bot: {e}")

    def get_bot(self, bot_id: str, user_id: str):
        try:
            # Query the Bots table for the given bot_id
            bot_query = (
                self.db.table("Bots")
                .select("*")
                .eq("id", bot_id)
                .eq("bot_type", "permanent")
                .execute()
            )
            bot_data = bot_query.data

            # If no bot is found, raise an error
            if not bot_data:
                raise HTTPException(
                    status_code=404, detail=f"No bot found with bot_id: {bot_id}"
                )

            bot = bot_data[0]  # Assuming a single bot matches the bot_id

            # Fetch engagement data for the specific bot_id
            engagement_query = (
                self.db.table("BotEngagement")
                .select("*")
                .eq("bot_id", bot_id)
                .execute()
            )
            engagement_data = engagement_query.data

            # Initialize metrics
            bot_metrics = {"unique_users": set(), "total_likes": 0, "message_count": 0}

            # Process engagements to collect metrics
            for engagement in engagement_data:
                bot_metrics["unique_users"].add(engagement["user_id"])
                bot_metrics["total_likes"] += 1 if engagement.get("likes") else 0
                bot_metrics["message_count"] += 1

            # Check if the bot is marked as favorite
            favorite_query = (
                self.db.table("favorite_bots")
                .select("*")
                .eq("bot_id", bot_id)
                .eq("favourite", True)
                .execute()
            )
            favorite_bot = bool(favorite_query.data)
            print(favorite_bot)
            # Get the current UTC time
            current_time = datetime.now(timezone.utc)
            one_week_ago = current_time - timedelta(days=7)

            # Parse created_at to determine if recently added
            created_at_str = bot["created_at"]
            created_at_date = CommonUtil.parse_timestamp(created_at_str)
            recently_added_tag = created_at_date > one_week_ago
            if user_id:
                bot_user_id = bot["user_id"] == user_id
            else:
                bot_user_id = False

            # Create a BotDetails instance with the required data
            bot_details = MyBotDetails(
                bot_id=bot["id"],
                name=bot["name"],
                description=bot["description"],
                created_by=bot["created_by"],
                likes_count=bot_metrics["total_likes"],
                message_count=bot_metrics["message_count"],
                unique_user_count=len(bot_metrics["unique_users"]),
                is_published=bot["is_published"],
                color_palette=bot["color_palette"],
                gpt_model=bot["gpt_model"],
                persona=bot["persona"],
                purpose=bot["purpose"],
                icon=bot["icon"],
                owner_flag=bot_user_id,  # Assume owner since only bot_id is passed
                is_favourite=favorite_bot,
                recently_added_tag=recently_added_tag,
            )

            return bot_details

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch bot information: {e}"
            )

    def update_bot(self, bot_id: str, bot_data: BotCreate):
        try:
            result = (
                self.db.table("Bots").update(bot_data.dict()).eq("id", bot_id).execute()
            )
            # Assuming result.data contains a list, extract the first item
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to create school: No data returned"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update bot: {e}")

    def delete_bot(self, bot_id: str):
        try:
            self.db.table("Bots").delete().eq("id", bot_id).execute()
            return {"message": "Bot deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete bot: {e}")

    def my_bots_informations(self, user_id) -> List[MyBotDetails]:
        try:
            # change the revert
            bots_response_data = (
                self.db.table("Bots")
                .select("*")
                .eq("user_id", user_id)
                .eq("bot_type", "permanent")
                .order("created_at", desc=True)
                .execute()
            )
            bots_response = bots_response_data.data

            engagement_response_data = (
                self.db.table("BotEngagement").select("*").execute()
            )
            engagement_response = engagement_response_data.data
            print(engagement_response)

            # Dictionary to store bot engagement metrics
            bot_metrics = defaultdict(
                lambda: {"unique_users": set(), "total_likes": 0, "message_count": 0}
            )

            # Process engagements to collect metrics
            for engagement in engagement_response:
                bot_id = engagement["bot_id"]

                # Update metrics for each bot
                bot_metrics[bot_id]["unique_users"].add(engagement["user_id"])
                bot_metrics[bot_id]["total_likes"] += 1 if engagement["likes"] else 0
                bot_metrics[bot_id]["message_count"] += 1

            # Get the current UTC time (timezone-aware)

            current_time = datetime.now(timezone.utc)

            # Calculate the one-week window (timezone-aware)

            one_week_ago = current_time - timedelta(days=7)

            # Finalize results by transforming sets to counts for unique user counts
            bot_engagement_stats = []
            for bot in bots_response:
                bot_id = bot["id"]
                metrics = bot_metrics[bot_id]

                # Parse created_at with fromisoformat and convert to date
                created_at_str = bot["created_at"]
                created_at_date = CommonUtil.parse_timestamp(created_at_str)

                # Determine if the bot was recently added
                added_tag = created_at_date > one_week_ago
                bot_user_id = bot["user_id"] == user_id

                fav_bot = (
                    self.db.table("favorite_bots")
                    .select("*")
                    .eq("bot_id", bot_id)
                    .eq("favourite", True)
                    .execute()
                )
                print("--------------", "The check for fav", "-----------------")
                print(fav_bot.data)
                if not fav_bot.data:
                    favorite_bot = False
                else:
                    favorite_bot = True

                # Create a BotDetails instance for each bot with the required data
                bot_details = MyBotDetails(
                    bot_id=bot_id,
                    name=bot["name"],
                    description=bot["description"],
                    created_by=bot["created_by"],
                    likes_count=metrics["total_likes"],
                    message_count=metrics["message_count"],
                    unique_user_count=len(metrics["unique_users"]),
                    is_published=bot["is_published"],
                    color_palette=bot["color_palette"],
                    gpt_model=bot["gpt_model"],
                    persona=bot["persona"],
                    purpose=bot["purpose"],
                    icon=bot["icon"],
                    owner_flag=bot_user_id,
                    is_favourite=favorite_bot,
                    recently_added_tag=added_tag,
                )

                bot_engagement_stats.append(bot_details)
            return bot_engagement_stats
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch bots information: {e}"
            )

    def community_bots_informations(self, user_id: str) -> List[BotDetails]:
        try:
            bots_response_data = (
                self.db.table("Bots")
                .select("*")
                .eq("is_published", True)
                .eq("bot_type", "permanent")
                .order("updated_at", desc=True)
                .order("created_at", desc=True)
                .execute()
            )
            bots_response = bots_response_data.data
            print(bots_response)
            engagement_response_data = (
                self.db.table("BotEngagement").select("*").execute()
            )
            engagement_response = engagement_response_data.data
            # Dictionary to store bot engagement metrics directly
            bot_metrics = defaultdict(
                lambda: {"unique_users": set(), "total_likes": 0, "message_count": 0}
            )

            # Process engagements to collect metrics
            for engagement in engagement_response:
                bot_id = engagement["bot_id"]

                # Update metrics for each bot
                bot_metrics[bot_id]["unique_users"].add(engagement["user_id"])
                bot_metrics[bot_id]["total_likes"] += 1 if engagement["likes"] else 0
                bot_metrics[bot_id]["message_count"] += 1

            # Finalize results by transforming sets to counts for unique user counts
            bot_engagement_stats = []
            for bot in bots_response:
                bot_id = bot["id"]
                metrics = bot_metrics[bot_id]
                bot_user_id = bot["user_id"] == user_id
                fav_bot = (
                    self.db.table("favorite_bots")
                    .select("*")
                    .eq("bot_id", bot_id)
                    .eq("favourite", True)
                    .execute()
                )
                print(fav_bot)
                if not fav_bot.data:
                    favorite_bot = False
                else:
                    favorite_bot = True

                # Create a BotDetails instance for each bot with the required data
                bot_details = BotDetails(
                    bot_id=bot_id,
                    name=bot["name"],
                    description=bot["description"],
                    created_by=bot["created_by"],
                    likes_count=metrics["total_likes"],
                    message_count=metrics["message_count"],
                    unique_user_count=len(metrics["unique_users"]),
                    is_published=bot["is_published"],
                    color_palette=bot["color_palette"],
                    gpt_model=bot["gpt_model"],
                    persona=bot["persona"],
                    purpose=bot["purpose"],
                    icon=bot["icon"],
                    owner_flag=bot_user_id,
                    is_favourite=favorite_bot,
                )
                bot_engagement_stats.append(bot_details)
            return bot_engagement_stats
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch bots information: {e}"
            )

    def mark_favourite_bots(self, bot_id: str, user_id: str):
        # Check if the bot is already a favorite for this user
        existing_favorite = (
            self.db.table("favorite_bots")
            .select("*")
            .eq("bot_id", bot_id)
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        if existing_favorite.data:
            check_fav = existing_favorite.data[0]["favourite"]
            if check_fav:
                self.db.table("favorite_bots").update({"favourite": False}).eq(
                    "bot_id", bot_id
                ).eq("user_id", user_id).execute()
                return {"message": "This bot is marked as unfavorite by the user."}
            else:
                self.db.table("favorite_bots").update({"favourite": True}).eq(
                    "bot_id", bot_id
                ).eq("user_id", user_id).execute()
                return {
                    "message": "This bot is already marked as favorite by the user."
                }
        # Retrieve the bot owner (creator's user_id) from the Bots table
        bot_info = self.db.table("Bots").select("user_id").eq("id", bot_id).execute()
        if not bot_info.data:
            raise HTTPException(status_code=404, detail="Bot not found.")

        owner_id = bot_info.data[0]["user_id"]

        # Insert a new favorite entry
        try:
            result = (
                self.db.table("favorite_bots")
                .insert(
                    {
                        "bot_id": bot_id,
                        "user_id": user_id,
                        "owner_id": owner_id,
                        "favourite": True,
                    }
                )
                .execute()
            )

            if result.data:
                return {"message": "Bot has been successfully marked as favorite."}
            else:
                raise Exception(
                    "Failed to mark bot as favorite due to an unexpected error."
                )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_favorite_bots(self, user_id: str) -> List[BotDetails]:
        # 1. Fetch all favorite bots for the user
        favorites_response = (
            self.db.table("favorite_bots")
            .select("bot_id")
            .eq("user_id", user_id)
            .eq("favourite", True)
            .execute()
        )
        favorite_bot_ids = [item["bot_id"] for item in favorites_response.data]

        # 2. Fetch bot details, message count, likes count, and unique user count
        favorite_bots = []
        for bot_id in favorite_bot_ids:
            # Fetch bot details
            bot_response = (
                self.db.table("Bots")
                .select(
                    "id",
                    "name",
                    "description",
                    "created_by",
                    "is_published",
                    "color_palette",
                    "gpt_model",
                    "persona",
                    "purpose",
                    "user_id",
                    "icon",
                )
                .eq("id", bot_id)
                .execute()
            )

            bot_data = bot_response.data[0] if bot_response.data else {}

            # Message count and unique user count
            engagement_response = (
                self.db.table("BotEngagement")
                .select("user_id", "messages_sent", "likes")
                .eq("bot_id", bot_id)
                .execute()
            )
            # Count non-empty `messages_sent` entries
            message_count = sum(
                1 for item in engagement_response.data if item["messages_sent"]
            )
            unique_user_count = len(
                {
                    item["user_id"]
                    for item in engagement_response.data
                    if item["user_id"]
                }
            )

            # Count `likes` where it is True
            likes_count = sum(
                1 for item in engagement_response.data if item["likes"] is True
            )

            bot_user_id = bot_data["user_id"] == user_id

            # Prepare the BotDetails data
            favorite_bots.append(
                BotDetails(
                    bot_id=bot_data.get("id", ""),
                    name=bot_data.get("name", ""),
                    description=bot_data.get("description", ""),
                    created_by=bot_data.get("created_by", ""),
                    likes_count=likes_count,
                    message_count=message_count,
                    unique_user_count=unique_user_count,
                    is_published=bot_data.get("is_published", False),
                    color_palette=bot_data.get("color_palette", ""),
                    gpt_model=bot_data.get("gpt_model", ""),
                    persona=bot_data.get("persona", ""),
                    purpose=bot_data.get("purpose", ""),
                    icon=bot_data.get("icon", ""),
                    owner_flag=bot_user_id,
                    is_favourite=True,
                )
            )

        return favorite_bots

    # def generate_system_instruction(data):
    #     # Mandatory identity statement
    #     instruction = f"You are a bot named {data['name']}."

    #     # Include role description if provided
    #     if data.get("description"):
    #         instruction += f" Your role is: {data['description']}."

    #     # Include persona details if provided
    #     if data.get("persona"):
    #         instruction += (
    #             f" You are characterized by the following persona: {data['persona']}."
    #         )

    #     # Include purpose if provided
    #     if data.get("purpose"):
    #         instruction += f" Your primary purpose is: {data['purpose']}."

    #     # Clarify expected behavior or additional instructions (optional generic guideline)
    #     instruction += " Be helpful, concise, and accurate in your responses."

    #     # Ensure proper formatting with trailing whitespace stripped
    #     return instruction.strip()

    def get_system_instruction(self, bot_id: str):
        response = (
            self.db.table("Bots")
            .select("name, description, persona, purpose")
            .eq("id", bot_id)
            .execute()
        )
        data = response.data[0]
        # Mandatory identity statement
        instruction = f"You are a bot named {data['name']}."

        # Include role description if provided
        if data.get("description"):
            instruction += f" Your role is: {data['description']}."

        # Include persona details if provided
        if data.get("persona"):
            instruction += (
                f" You are characterized by the following persona: {data['persona']}."
            )

        # Include purpose if provided
        if data.get("purpose"):
            instruction += f" Your primary purpose is: {data['purpose']}."

        # Add guardrails for questions outside the intended purpose
        instruction += (
            " You are expected to answer only questions that align with your role and purpose. "
            "If asked a question that seems unrelated to these, respond politely by stating your area of focus "
            "and suggest consulting an expert in the relevant field."
        )

        # Clarify expected behavior or additional instructions (optional generic guideline)
        instruction += " Be helpful, concise, and accurate in your responses. "

        return instruction

    def get_updated_system_instruction(self, bot_id: str):
        response = (
            self.db.table("Bots")
            .select("temp_name, temp_description, temp_persona, temp_purpose")
            .eq("id", bot_id)
            .execute()
        )
        data = response.data[0]
        # Mandatory identity statement
        temp_instruction = f"You are a bot named {data['temp_name']}."

        # Include role description if provided
        if data.get("temp_description"):
            temp_instruction += f" Your role is: {data['temp_description']}."

        # Include persona details if provided
        if data.get("temp_persona"):
            temp_instruction += f" You are characterized by the following persona: {data['temp_persona']}."

        # Include purpose if provided
        if data.get("temp_purpose"):
            temp_instruction += f" Your primary purpose is: {data['temp_purpose']}."

        # Add guardrails for questions outside the intended purpose
        temp_instruction += (
            " You are expected to answer only questions that align with your role and purpose. "
            "If asked a question that seems unrelated to these, respond politely by stating your area of focus "
            "and suggest consulting an expert in the relevant field."
        )

        # Clarify expected behavior or additional instructions (optional generic guideline)
        temp_instruction += " Be helpful, concise, and accurate in your responses."

        return temp_instruction

    def get_model_info(self, bot_id: str):
        response = self.db.table("Bots").select("gpt_model").eq("id", bot_id).execute()
        data = response.data[0]
        model_information = data["gpt_model"]
        return model_information

    def mark_publish_bot(self, bot_id: str, publish: bool):
        # Try to mark the chat_msg_id as favorite
        response = (
            self.db.table("Bots")
            .update({"is_published": publish})
            .eq("id", bot_id)
            .execute()
        )
        print(response)

        if response and response.data:
            if publish:
                print(f"Marked is_published {bot_id} as True!")
            else:
                print(f"Unmarked is_published {bot_id} as False!")

        return True

    def bot_edit_input_data(self, bot_id: str) -> BotEditData:
        response = (
            self.db.table("Bots")
            .select(
                "name, description, persona, purpose, icon, color_palette, gpt_model, is_published, created_by, user_id"
            )
            .eq("id", bot_id)
            .execute()
        )

        response_data = response.data[0]

        name = response_data["name"]
        description = response_data["description"]
        persona = response_data["persona"]
        purpose = response_data["purpose"]
        icon = response_data["icon"]
        color_palette = response_data["color_palette"]
        gpt_model = response_data["gpt_model"]
        is_published = response_data["is_published"]
        created_by = response_data["created_by"]
        user_id = response_data["user_id"]

        bot_edit_data = BotEditData(
            name=name,
            description=description,
            persona=persona,
            purpose=purpose,
            icon=icon,
            color_palette=color_palette,
            gpt_model=gpt_model,
            is_published=is_published,
            created_by=created_by,
            user_id=user_id,
        )

        return bot_edit_data

    def generate_bot_id(self) -> str:
        return str(uuid.uuid4())

    # def update_bot_details(
    #     self,
    #     bot_id,
    #     name,
    #     description,
    #     persona,
    #     purpose,
    #     icon,
    #     color_palette,
    #     gpt_model,
    #     scope,
    #     bot_type,
    # ) -> CreateBotInfo:
    #     try:
    #         if bot_type == "temporary":
    #             values = {
    #                 "temp_name": name,
    #                 "temp_description": description,
    #                 "temp_persona": persona,
    #                 "temp_purpose": purpose,
    #                 "temp_icon": icon,
    #                 "temp_color_palette": color_palette,
    #                 "temp_gpt_model": gpt_model,
    #                 "temp_scope": scope,
    #             }
    #             result = self.db.table("Bots").update(values).eq("id", bot_id).execute()
    #         else:
    #             values = {
    #                 "name": name,
    #                 "description": description,
    #                 "persona": persona,
    #                 "purpose": purpose,
    #                 "icon": icon,
    #                 "color_palette": color_palette,
    #                 "gpt_model": gpt_model,
    #                 "scope": scope,
    #             }
    #             result = self.db.table("Bots").update(values).eq("id", bot_id).execute()

    #         # Assuming result.data contains a list, extract the first item
    #         if result.data:
    #             return CreateBotInfo(id=bot_id, bot_type=bot_type)
    #         else:
    #             raise HTTPException(
    #                 status_code=500,
    #                 detail="Failed to update bot information: No data returned",
    #             )
    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=500, detail=f"Failed to update bot information: {e}"
    #         )

    def create_iframe_id(self, bot_id: str) -> CreateIframeInfo:
        response = (
            self.db.table("iframe_details").select("*").eq("bot_id", bot_id).execute()
        )
        response_data = response.data
        if response_data:
            existing_iframe_id = response_data[0]["iframe_id"]
            return CreateIframeInfo(iframe_id=existing_iframe_id, bot_id=bot_id)
        else:
            iframe_id = self.generate_bot_id()
            values = {"iframe_id": iframe_id, "bot_id": bot_id}
            try:
                result = self.db.table("iframe_details").insert(values).execute()

                if result.data:
                    return CreateIframeInfo(iframe_id=iframe_id, bot_id=bot_id)
                else:
                    raise HTTPException(
                        status_code=500, detail="Failed to create bot: No data returned"
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Failed to create IframeId for bot: {e}"
                )

    def check_iframe_id(self, iframe_id: str):
        """
        Checks if an iframe_id exists in the database table.

        Args:
        iframe_id (str): The iframe ID to check.

        Returns:
        tuple: A tuple (exists, data), where:
            - exists (bool): True if iframe_id exists, False otherwise.
            - data (list): The data associated with the iframe_id if it exists, otherwise an empty list.
        """
        try:
            # Execute the database query
            response = (
                self.db.table("iframe_details")
                .select("*")
                .eq("iframe_id", iframe_id)
                .execute()
            )
            response_data = response.data
            print("response_data", response_data)
            # Check if the response data is empty or not
            if response_data:  # Non-empty list means iframe_id exists
                return True
            else:  # Empty list means iframe_id does not exist
                return False

        except Exception as e:
            # Log the exception and return a default failure response
            print(f"An error occurred while checking iframe_id: {e}")
            return False

    def get_session_id_for_iframe(self, iframe_id: str, finger_print_id: str):
        try:
            # Query the BotEngagement table for a matching session
            response = (
                self.db.table("BotEngagement")
                .select("id")
                .eq("iframe_id", iframe_id)
                .eq("finger_print_id", finger_print_id)
                .execute()
            )
            response_data = response.data
            # Check if response data exists and return the session ID
            if response_data:
                return response_data[0]["id"]
            # If no matching session, return None
            return None
        except Exception as e:
            # Handle any errors and log the exception
            print(f"Error occurred while fetching session ID: {e}")
            return None

    def get_session_id_for_logged_in_iframe(self, iframe_id: str, user_id: str):
        try:
            # Query the BotEngagement table for a matching session
            response = (
                self.db.table("BotEngagement")
                .select("id")
                .eq("iframe_id", iframe_id)
                .eq("user_id", user_id)
                .execute()
            )
            response_data = response.data
            # Check if response data exists and return the session ID
            if response_data:
                return response_data[0]["id"]
            # If no matching session, return None
            return None
        except Exception as e:
            # Handle any errors and log the exception
            print(f"Error occurred while fetching session ID: {e}")
            return None

    def delete_iframe(self, iframe_id: str, user_id: str):
        try:
            # Step 1: Find the session ID in BotEngagement
            response = (
                self.db.table("BotEngagement")
                .select("id")
                .eq("iframe_id", iframe_id)
                .eq("user_id", user_id)
                .execute()
            )
            if not response.data:
                return f"No session found for iframe_id: {iframe_id} and user_id: {user_id}"

            session_id = response.data[0]["id"]  # Assuming only one record matches

            # Step 2: Delete related chat records from Bots_chat_record
            self.db.table("Bots_chat_record").delete().eq(
                "bot_session_id", session_id
            ).execute()

            # Step 3: Delete the session from BotEngagement
            self.db.table("BotEngagement").delete().eq("id", session_id).execute()

            return f"Successfully deleted session and chat records for iframe_id: {iframe_id} and user_id: {user_id}"

        except Exception as e:
            return f"An error occurred: {str(e)}"

    def delete_iframe_for_not_logged(self, iframe_id: str, finger_print_id: str):
        try:
            # Step 1: Find the session ID in BotEngagement
            response = (
                self.db.table("BotEngagement")
                .select("id")
                .eq("iframe_id", iframe_id)
                .eq("finger_print_id", finger_print_id)
                .execute()
            )
            if not response.data:
                return f"No session found for iframe_id: {iframe_id} and finger_print_id: {finger_print_id}"

            session_id = response.data[0]["id"]  # Assuming only one record matches

            # Step 2: Delete related chat records from Bots_chat_record
            self.db.table("Bots_chat_record").delete().eq(
                "bot_session_id", session_id
            ).execute()

            # Step 3: Delete the session from BotEngagement
            self.db.table("BotEngagement").delete().eq("id", session_id).execute()

            return f"Successfully deleted session and chat records for iframe_id: {iframe_id} and finger_print_id: {finger_print_id}"

        except Exception as e:
            return f"An error occurred: {str(e)}"

    def update_fingerprint(
        self, session_id: str, iframe_id: str, user_id: str, finger_print_id: str
    ):
        try:
            response = (
                self.db.table("BotEngagement")
                .select("finger_print_id")
                .eq("id", session_id)
                .eq("user_id", user_id)
                .eq("iframe_id", iframe_id)
                .execute()
            )
            get_fingerprint_id = response.data[0]["finger_print_id"]
            # Step 4: Compare the fingerprint_id
            if get_fingerprint_id == finger_print_id:
                return "The provided fingerprint_id is the same as the existing one. No update needed."

            # Step 5: Update the fingerprint_id
            update_result = (
                self.db.table("BotEngagement")
                .update({"finger_print_id": finger_print_id})
                .eq("id", session_id)
                .execute()
            )
            if update_result.data:
                return f"Successfully updated fingerprint_id for record with ID: {session_id}."
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update fingerprint_id: No data returned",
                )
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def fetch_iframe_bot_history_external_user(
        self, iframe_id: str, finger_print_id: str
    ):
        try:
            # Search by iframe_id and finger_print_id
            engagement_response = (
                self.db.table("BotEngagement")
                .select("id")
                .eq("iframe_id", iframe_id)
                .eq("finger_print_id", finger_print_id)
                .is_("user_id", None)
                .execute()
            )

            # Extract bot_session_id from response
            engagement_data = engagement_response.data
            if not engagement_data:
                return {
                    "message": "No BotEngagement records found for the provided parameters."
                }

            bot_session_id = engagement_data[0]["id"]

            # Query Bots_chat_record table to fetch chat records based on bot_session_id
            chat_response = (
                self.db.table("Bots_chat_record")
                .select("*")
                .eq("bot_session_id", bot_session_id)
                .execute()
            )

            # Return chat history
            chat_data = chat_response.data
            return (
                chat_data
                if chat_data
                else {"message": "No chat records found for the given bot session ID."}
            )

        except Exception as e:
            return {"error getting history": str(e)}

    def fetch_iframe_bot_history_internal_user(
        self,
        user_id: str,
        iframe_id: str,
    ):
        try:
            engagement_response = (
                self.db.table("BotEngagement")
                .select("id")
                .eq("user_id", user_id)
                .eq("iframe_id", iframe_id)
                .execute()
            )

            # Extract bot_session_id from response
            engagement_data = engagement_response.data
            if not engagement_data:
                return {
                    "message": "No BotEngagement records found for the provided parameters."
                }

            bot_session_id = engagement_data[0]["id"]

            # Query Bots_chat_record table to fetch chat records based on bot_session_id
            chat_response = (
                self.db.table("Bots_chat_record")
                .select("*")
                .eq("bot_session_id", bot_session_id)
                .execute()
            )

            # Return chat history
            chat_data = chat_response.data
            return (
                chat_data
                if chat_data
                else {"message": "No chat records found for the given bot session ID."}
            )

        except Exception as e:
            return {"error getting history": str(e)}
