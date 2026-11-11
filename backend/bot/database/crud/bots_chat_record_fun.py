from bot.database.manager import DatabaseManager


class Bot_Chat_Record:
    def __init__(self):
        self.db = DatabaseManager().get_client()

    def add_chat_record(
        self, chat_id: str, chat_message: str, bot_response: str, bot_session_id: str
    ):
        values = {
            "chat_id": chat_id,
            "chat_message": chat_message,
            "bot_response": bot_response,
            "bot_session_id": bot_session_id,
        }

        try:
            self.db.table("Bots_chat_record").insert(values).execute()
            print("The chat record of bot is added successfully")
        except Exception as e:
            print(e)

    def add_bot_engagment(
        self,
        id: str,
        bot_id: str,
        user_id: str,
        messages_sent: str,
        iframe_id: str,
        finger_print_id: str,
    ):
        values = {
            "id": id,
            "bot_id": bot_id,
            "user_id": user_id,
            "messages_sent": messages_sent,
            "iframe_id": iframe_id,
            "finger_print_id": finger_print_id,
        }
        try:
            self.db.table("BotEngagement").insert(values).execute()
            print(
                "The chat session of bot in the form of engagment is added successfully"
            )
        except Exception as e:
            print(e)
