from fastapi import APIRouter, Depends, Request, HTTPException, WebSocket, Query, status
from bot.database.schemas.bot import BotCreate, Bot, IframeInfoRequest, IframeBotHistory
from bot.database.crud.bot import BotCRUD
from security.auth import user_name_token
from fastapi.responses import JSONResponse
from bot.database.crud.bot_chat import Bot_chat_agent
import asyncio
from security.auth import get_or_verify_token, update_activity
from typing import Dict, Optional
import os
from dotenv import load_dotenv
from security.auth import verify_token


load_dotenv()

bots = APIRouter(prefix="/api/bots_creations", tags=["Bots"])


class BotChatProcessor:
    """
    Processor to process each conversation
    """

    def __init__(
        self,
        socket: WebSocket,
        bot_chat_agent: Bot_chat_agent,
        bot_id: str,
        token: Optional[str] = None,
        user_id: Optional[str] = None,
        bot_type: Optional[str] = None,
        iframe_id: Optional[str] = None,
        finger_print_id: Optional[str] = None,
        reset: Optional[bool] = None,
    ):
        self.socket = socket
        self.bot_chat_agent = bot_chat_agent
        self.token = token
        self.bot_id = bot_id
        self.user_id = user_id
        self.bot_type = bot_type
        self.iframe_id = iframe_id
        self.finger_print_id = finger_print_id
        self.reset = reset

    async def process(self):
        print("Prepearing to send response of bot")
        try:
            while True:
                msg = await self.bot_chat_agent.response_queue.get()
                await self.socket.send_text(msg)
                self.bot_chat_agent.response_queue.task_done()
        except asyncio.CancelledError:
            print("Processing task was cancelled")

    async def start(self):
        processing_task = asyncio.create_task(self.process())
        try:
            while True:
                msg = await self.socket.receive_text()
                print("msg----------", msg)
                if self.token:
                    asyncio.create_task(update_activity(self.token))
                await self.bot_chat_agent.bot_chat(
                    bot_id=self.bot_id,
                    query=msg,
                    user_id=self.user_id,
                    bot_type=self.bot_type,
                    iframe_id=self.iframe_id,
                    finger_print_id=self.finger_print_id,
                    reset=self.reset,
                )
        except Exception as e:
            print(f"WebSocket connection closed with exception: {e}")
        finally:
            processing_task.cancel()
            await processing_task
            print("Cleaned up processing task")


class BotChatManager:
    """
    A class to manage all the conversations which are happening
    """

    def __init__(self):
        self.active_bot_connection: Dict[str, BotChatProcessor] = {}

    def get_chat_processor(self, user_id: str) -> Optional[BotChatProcessor]:
        return self.active_bot_connection.get(user_id)

    def add_chat_processor(
        self,
        user_id: str,
        processor: BotChatProcessor,
    ):
        self.active_bot_connection[user_id] = processor

    def remove_chat_processor(self, user_id: str):
        if user_id in self.active_bot_connection:
            del self.active_bot_connection[user_id]
            print(f"Removed processor for {user_id}")


class IframeBotChatManager:
    """
    A class to manage all the conversations which are happening
    """

    def __init__(self):
        self.active_bot_connection: Dict[str, BotChatProcessor] = {}

    def get_chat_processor(self, finger_print_id: str) -> Optional[BotChatProcessor]:
        return self.active_bot_connection.get(finger_print_id)

    def add_chat_processor(
        self,
        finger_print_id: str,
        processor: BotChatProcessor,
    ):
        self.active_bot_connection[finger_print_id] = processor

    def remove_chat_processor(self, finger_print_id: str):
        if finger_print_id in self.active_bot_connection:
            del self.active_bot_connection[finger_print_id]
            print(f"Removed processor for {finger_print_id}")


def get_bot_chat_manager():
    if not hasattr(get_bot_chat_manager, "instance"):
        get_bot_chat_manager.instance = BotChatManager()
    return get_bot_chat_manager.instance


def get_iframe_bot_chat_manager():
    if not hasattr(get_iframe_bot_chat_manager, "instance"):
        get_iframe_bot_chat_manager.instance = IframeBotChatManager()
    return get_iframe_bot_chat_manager.instance


def get_bot_crud():
    return BotCRUD()


@bots.post("/bots")
async def create_bot_endpoint(
    request: Request,
    bot: BotCreate,
    bot_type: str | None = Query(default=None),
    bot_embedding_id: str | None = Query(default=None),
    user: str = Depends(user_name_token),
    bot_crud: BotCRUD = Depends(get_bot_crud),
):
    user_id = request.state.user_id
    user_name = user
    print(user_name)
    if bot_type == "preview":
        bot_type = "temporary"
    else:
        bot_type = "permanent"
    try:
        bot_create = bot_crud.create_bot(
            id=bot.bot_id,
            name=bot.name,
            description=bot.description,
            persona=bot.persona,
            purpose=bot.purpose,
            icon=bot.icon,
            color_palette=bot.color_palette,
            gpt_model=bot.gpt_model,
            is_published=bot.is_published,
            scope=bot.scope,
            created_by=user_name,
            user_id=user_id,
            bot_type=bot_type,
            bot_embedding_id=bot_embedding_id,
        )
        return bot_create
    except Exception as e:
        # Log the error and raise an HTTPException with a 500 status code
        error_message = f"Failed to create bot: {e}"
        print(
            error_message
        )  # In production, you might replace this with proper logging
        raise HTTPException(status_code=500, detail=error_message)


@bots.get("/bots/{bot_id}")
async def read_bot(
    request: Request, bot_id: str, bot_crud: BotCRUD = Depends(get_bot_crud)
):
    # Check for token in headers to confirm it's an external user
    token = request.headers.get("token")
    if not token:
        return bot_crud.get_bot(bot_id=bot_id, user_id=None)
    else:
        user_id = verify_token(token)
        if not user_id:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)
        else:
            return bot_crud.get_bot(bot_id=bot_id, user_id=user_id)


@bots.put("/bots/{bot_id}", response_model=Bot)
async def update_bot_endpoint(
    bot_id: str, bot: BotCreate, bot_crud: BotCRUD = Depends(get_bot_crud)
):
    return bot_crud.update_bot(bot_id, bot)


@bots.delete("/bots/{bot_id}")
async def delete_bot_endpoint(bot_id: str, bot_crud: BotCRUD = Depends(get_bot_crud)):
    return bot_crud.delete_bot(bot_id)


@bots.get("/my_bots_information")
async def get_total_my_bots_informations(
    request: Request, bot_crud: BotCRUD = Depends(get_bot_crud)
):
    user_id = request.state.user_id
    return bot_crud.my_bots_informations(user_id=user_id)


@bots.options("/community_bots_information")
async def options_handler():
    return JSONResponse(content={}, status_code=204)


@bots.get("/community_bots_information")
async def get_total_community_bots_informations(
    request: Request, bot_crud: BotCRUD = Depends(get_bot_crud)
):
    user_id = request.state.user_id
    return bot_crud.community_bots_informations(user_id=user_id)


@bots.get("/favourite_bots_information")
async def get_total_favourite_bots_informations(
    request: Request, bot_crud: BotCRUD = Depends(get_bot_crud)
):
    user_id = request.state.user_id
    return bot_crud.get_favorite_bots(user_id=user_id)


@bots.post("/mark_favorite-bot/{bot_id}")
async def mark_favorite_bot(
    request: Request, bot_id: str, bot_crud: BotCRUD = Depends(get_bot_crud)
):
    user_id = request.state.user_id

    # Mark the bot as favorite
    response = bot_crud.mark_favourite_bots(bot_id=bot_id, user_id=user_id)

    return response


@bots.websocket("/bot_chat")
async def chat_with_bot(
    socket: WebSocket,
    bot_id: str | None = Query(default=None),
    bot_type: str | None = Query(default=None),
    iframe_id: str | None = Query(default=None),
    finger_print_id: str | None = Query(default=None),
    reset: bool | None = Query(default=None),
    user: str = Depends(get_or_verify_token),
    chat_manager: BotChatManager = Depends(get_bot_chat_manager),
    iframe_chat_manager: IframeBotChatManager = Depends(get_iframe_bot_chat_manager),
):
    bot_info = BotCRUD()
    user_id = user.get("user_id")
    print("user_id-----------", user_id, "----------------")
    # If user_id is missing, check iframe_id if provided
    if not user_id:
        print("the ist loop")
        if iframe_id:
            print("the second loop")
            try:
                exists = bot_info.check_iframe_id(iframe_id)
                print("exists --------", exists)
                if reset:
                    delete_result = bot_info.delete_iframe_for_not_logged(
                        iframe_id, finger_print_id
                    )
                    # Check if deletion was successful
                    if "Successfully deleted" in delete_result:
                        print(f"Successful during deletion: {delete_result}")
                    else:
                        print(f"Error during deletion: {delete_result}")
                if not exists:  # iframe_id does not exist
                    print("the third loop")
                    await socket.close(
                        code=1008
                    )  # Close WebSocket connection with policy violation code
                    return
            except Exception as e:
                print(f"Error checking iframe_id: {e}")
                await socket.close(code=1011)  # Internal error
                return
        else:
            print("the 4th loop")
            # No user_id and no iframe_id to check
            await socket.close(
                code=1008
            )  # Close WebSocket connection with policy violation code
            return
    if iframe_id and finger_print_id and user_id:
        delete_result = bot_info.delete_iframe(iframe_id, user_id)

        # Check if deletion was successful
        if "Successfully deleted" in delete_result:
            # Generate a new session ID
            print(f"NoError during deletion: {delete_result}")
        else:
            print(f"Error during deletion: {delete_result}")

    # If user_id exists or iframe_id is valid, proceed to accept the connection
    await socket.accept()
    try:
        model_info = bot_info.get_model_info(bot_id=bot_id)
        print("---------------", model_info, "---------------")
        print("---------++++++++++++++++")
        print("----------------", bot_id, "-------------------")
        agent_api_key = os.getenv("AZURE_API_KEY")
        bot_chat = Bot_chat_agent(model=model_info, apikey=agent_api_key)
        print(type(bot_chat))

        # # Create a session_id for the current user session
        # # Case 1: Only `user_id` exists
        # if user_id and not iframe_id and not finger_print_id:
        #     session_bot_id = bot_chat.generate_bot_chat_id()
        #     print("-------------", session_bot_id, "------------------")
        # # Case 2: Only `iframe_id` and `finger_print_id` exist
        # elif not user_id and iframe_id and finger_print_id:
        #     # Check if session_id exists for iframe_id and finger_print_id
        #     session_id = bot_info.get_session_id_for_iframe(iframe_id, finger_print_id)
        #     if session_id is None:
        #         # Create a new session_id
        #         session_flag = "new"
        #         session_bot_id = bot_chat.generate_bot_chat_id()
        #         print("-------------", session_bot_id, "------------------")
        #     else:
        #         session_flag = "old"
        #         session_bot_id = session_id
        # # Case 3: All three parameters exist
        # elif user_id and iframe_id and finger_print_id:
        #     session_id = bot_info.get_session_id_for_logged_in_iframe(
        #         iframe_id, user_id
        #     )
        #     if session_id is None:
        #         # Create a new session_id
        #         session_flag = "new"
        #         session_bot_id = bot_chat.generate_bot_chat_id()
        #         print("-------------", session_bot_id, "------------------")
        #     elif reset:
        #         session_flag = "reset"
        #         session_bot_id = bot_chat.generate_bot_chat_id()
        #         print("-------------", session_bot_id, "------------------")
        #     else:
        #         session_flag = "old"
        #         session_bot_id = session_id

        if user_id:
            processor = chat_manager.get_chat_processor(user_id)
            print("-------------", processor, "------------------")
            if processor is None:
                print(f"creating new processor for {user_id}")
                processor = BotChatProcessor(
                    socket=socket,
                    bot_chat_agent=bot_chat,
                    token=user.get("token"),
                    bot_id=bot_id,
                    user_id=user_id,
                    bot_type=bot_type,
                    iframe_id=iframe_id,
                    finger_print_id=finger_print_id,
                    reset=reset,
                )
                chat_manager.add_chat_processor(user_id, processor)

            try:
                await processor.start()
            finally:
                chat_manager.remove_chat_processor(user_id)
                print(f"Connection closed for {user_id}")
        else:
            print("processor loop")
            processor = iframe_chat_manager.get_chat_processor(finger_print_id)
            print("-------------", processor, "------------------")
            if processor is None:
                print(f"creating new processor for {finger_print_id}")
                processor = BotChatProcessor(
                    socket=socket,
                    bot_chat_agent=bot_chat,
                    token=user.get("token"),
                    bot_id=bot_id,
                    user_id=user_id,
                    bot_type=bot_type,
                    iframe_id=iframe_id,
                    finger_print_id=finger_print_id,
                )
                iframe_chat_manager.add_chat_processor(finger_print_id, processor)
                print("the adding happened")

            try:
                await processor.start()
            finally:
                iframe_chat_manager.remove_chat_processor(finger_print_id)
                print(f"Connection closed for {finger_print_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Response: {e}")


@bots.put("/publishing_bot/{bot_id}")
async def publish_bot(bot_id: str, bot_crud: BotCRUD = Depends(get_bot_crud)):
    try:
        success = bot_crud.mark_publish_bot(bot_id=bot_id, publish=True)
        if success:
            return {"message": f"Bot {bot_id} marked as favorite!"}
        else:
            raise HTTPException(status_code=500, detail="Failed to mark as favorite.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@bots.get("/bot_edit_data/{bot_id}")
async def edit_input_data(bot_id: str, bot_crud: BotCRUD = Depends(get_bot_crud)):
    edit_form_data = bot_crud.bot_edit_input_data(bot_id=bot_id)

    if edit_form_data is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Bot data not found for the given bot id"},
        )
    return edit_form_data


# @bots.put("/update_bots_info/{bot_id}")
# async def update_bot_information(
#     bot: UpdateBotInfo,
#     bot_id: str,
#     bot_type: str | None = Query(default=None),
#     bot_crud: BotCRUD = Depends(get_bot_crud),
# ):
#     if bot_type == "preview":
#         bot_type = "temporary"
#     else:
#         bot_type = "permanent"
#     try:
#         bot_create = bot_crud.update_bot_details(
#             bot_id=bot_id,
#             name=bot.name,
#             description=bot.description,
#             persona=bot.persona,
#             purpose=bot.purpose,
#             icon=bot.icon,
#             color_palette=bot.color_palette,
#             gpt_model=bot.gpt_model,
#             scope=bot.scope,
#             bot_type=bot_type,
#         )
#         return bot_create
#     except Exception as e:
#         # Log the error and raise an HTTPException with a 500 status code
#         error_message = f"Failed to update bot info: {e}"
#         print(
#             error_message
#         )  # In production, you might replace this with proper logging
#         raise HTTPException(status_code=500, detail=error_message)


@bots.post("/create_iframe_body")
async def bot_iframe_info(
    iframe_info: IframeInfoRequest, bot_crud: BotCRUD = Depends(get_bot_crud)
):
    response = bot_crud.create_iframe_id(iframe_info.bot_id)
    return response


@bots.post("/iframe_bot_history")
async def bot_iframe_history(
    request: Request,
    iframe_bot_history_info: IframeBotHistory,
    bot_crud: BotCRUD = Depends(get_bot_crud),
):
    try:
        # Check for token in headers to confirm it's an external user
        token = request.headers.get("token")
        if not token:
            # External user logic
            response = bot_crud.fetch_iframe_bot_history_external_user(
                iframe_bot_history_info.iframe_id,
                iframe_bot_history_info.finger_print_id,
            )
        else:
            user_id = verify_token(token)
            if not user_id:
                return JSONResponse({"detail": "Invalid token"}, status_code=401)
            else:
                # Internal user logic
                response = bot_crud.fetch_iframe_bot_history_internal_user(
                    user_id, iframe_bot_history_info.iframe_id
                )

        # Shared error handling
        messages = [
            "No BotEngagement records found for the provided parameters.",
            "No chat records found for the given bot session ID.",
        ]
        if any(message in response for message in messages):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Some fetching issue"
            )

        return response  # Success: return the data as is

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting history: {str(e)}",
        )
