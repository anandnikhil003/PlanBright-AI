from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, Query
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import JSONResponse, Response
from agents.feedback_generator import (
    FeedbackGenerator,
    get_feedback_generator,
    Feedbackchat,
)
import asyncio
from db.remote_storage import SupabaseStorage, get_storage
from models.data_models import (
    FeedbackData,
    InteractionResponseFeedback,
    TranslationLanguageRequest,
    GenerateFeedback,
    EditQuery,
)
from db.interaction_manager import InteractionManager, get_interaction_manager
from config.utils import (
    generate_pdf_from_markdown,
    generate_docx_from_markdown,
    generate_google_docs,
)
from config.utils import process_and_save_response
from config.agent_details import AGENT_DETAILS
from typing import Dict, Optional, Any
from security.auth import get_or_verify_token, update_activity


feedback_generator_router = APIRouter(
    prefix="/api/feedback_generator", tags=["Feedback Generator"]
)


class ChatProcessor:
    """
    Processor to process each conversation
    """

    def __init__(
        self,
        socket: WebSocket,
        feedback_chat: Feedbackchat,
        history_id: str,
        token: str,
        agent_details: Dict[str, Any],
        chat_id: Optional[str] = None,
    ):
        self.socket = socket
        self.coach = feedback_chat
        self.history_id = history_id
        self.token = token
        self.chat_id = chat_id
        self.agent_details = agent_details

    async def process(self):
        print("preparing to send responses")
        try:
            while True:
                msg = await self.coach.response_queue.get()
                await self.socket.send_text(msg)
                self.coach.response_queue.task_done()
        except asyncio.CancelledError:
            print("Processing task was cancelled")

    async def start(self):
        processing_task = asyncio.create_task(self.process())
        try:
            while True:
                msg = await self.socket.receive_text()
                asyncio.create_task(update_activity(self.token))
                await self.coach.chat(
                    query=msg,
                    feedback_history_id=self.history_id,
                    agent_details=self.agent_details,
                    chat_id=self.chat_id,
                )
        except Exception as e:
            print(f"WebSocket connection closed with exception: {e}")
        finally:
            processing_task.cancel()
            await processing_task
            print("Cleaned up processing task")


class ChatManager:
    """
    A class to manage all the conversations which are happening
    """

    def __init__(self):
        self.active_connections: Dict[str, ChatProcessor] = {}

    def get_chat_processor(self, user_id: str) -> Optional[ChatProcessor]:
        return self.active_connections.get(user_id)

    def add_chat_processor(
        self,
        user_id: str,
        processor: ChatProcessor,
    ):
        self.active_connections[user_id] = processor

    def remove_chat_processor(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"Removed processor for {user_id}")


def get_chat_manager():
    if not hasattr(get_chat_manager, "instance"):
        get_chat_manager.instance = ChatManager()
    return get_chat_manager.instance


@feedback_generator_router.post("/generate")
async def generate_iep(
    request: Request,
    feedback: GenerateFeedback,
    generator: FeedbackGenerator = Depends(get_feedback_generator),
    storage: SupabaseStorage = Depends(get_storage),
    interaction_manager: InteractionManager = Depends(get_interaction_manager),
):
    user_id = request.state.user_id
    try:
        return EventSourceResponse(
            content=generator.generate_feedback(
                query=feedback.user_query,
                remote_storage=storage,
                user_id=user_id,
                interaction_manager=interaction_manager,
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Response: {e}")


@feedback_generator_router.get("/history")
async def get_feedback_id_list(
    request: Request,
    storage: SupabaseStorage = Depends(get_storage),
):
    user_id = request.state.user_id
    try:
        agent_details = AGENT_DETAILS["feedback_generator"]
        table_name = agent_details["table_name_one"]
        id_column = agent_details["id_column_one"]

        # Fetch chat history for the given user_id
        feedback_id_history = storage.get_id_list(user_id, table_name, id_column)

        # Return the chat history
        return feedback_id_history
    except Exception as e:
        print("The error is:", str(e))


@feedback_generator_router.get("/history_list/{feedback_id}")
async def get_feedback_plan(
    feedback_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        agent_details = AGENT_DETAILS["feedback_generator"]
        feedback_plan_history = storage.get_agent_plan(feedback_id, agent_details)
        if feedback_plan_history is None:
            return JSONResponse(
                status_code=404, content={"message": "Feedback Plan not found"}
            )
        # Return the chat history
        return feedback_plan_history
    except Exception as e:
        print("The error is:", str(e))


@feedback_generator_router.put("/edit_history_title/{feedback_id}")
async def edit_history_title(
    feedback_id: str,
    edited_msg: EditQuery,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    edited_response = storage.title_edit(
        feedback_id, edited_msg.edited_query, agent_details
    )

    if edited_response:
        return {"message": "Edited user query successfully!"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to edit usery query as no iep history ID: {feedback_id} exist",
        )


@feedback_generator_router.delete("/delete_history/{history_id}")
async def delete_history(
    history_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    delete_response = storage.delete_history_chat(history_id, agent_details)
    if delete_response is None:
        return {"message": "history deleted successfully!"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to delete as no chat message ID: {history_id} exist",
        )


@feedback_generator_router.delete("/clear_all_history")
async def clear_all_history(
    request: Request,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        user_id = request.state.user_id
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        agent_details = AGENT_DETAILS["feedback_generator"]
        response = storage.delete_all_history(user_id, agent_details)
        if response.get("message") == "No chat history found for the user.":
            return {"message": "No chat history found for the user."}
        elif response.get("message") == "All chat history deleted successfully!":
            return {"message": "All chat history deleted successfully!"}
        else:
            raise HTTPException(status_code=500, detail=response.get("message"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@feedback_generator_router.put("/update_feedback/{feedback_id}")
async def add_feedback(
    feedback_id: str,
    feedback: FeedbackData,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    udpdated_response = storage.update_feedback(
        feedback_id, feedback.feedback, feedback.feedback_description, agent_details
    )
    if udpdated_response is None:
        return {"message": "Feedback updated successfully!"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to update feedback as no IEP ID: {feedback_id} exist",
        )


@feedback_generator_router.get("/download/{feedback_id}")
async def download_feedback(
    feedback_id: str,
    remote_storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    feedback_content = remote_storage.get_response_by_id(
        id=feedback_id, agent_details=agent_details
    )

    if feedback_content is None:
        return JSONResponse(status_code=404, content={"message": "IEP not found"})
    return Response(
        content=feedback_content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={feedback_id}.md"},
    )


@feedback_generator_router.get("/download_pdf/{feedback_id}")
async def download_feedback_content_pdf(
    feedback_id: str,
    remote_storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    first_table_name = agent_details["table_name_one"]
    second_table_name = agent_details["table_name_two"]
    third_tabel_name = agent_details["table_name_three"]
    id_column_one = agent_details["id_column_one"]
    id_column_two = agent_details["id_column_two"]
    model = agent_details["model"]
    response_field_one = agent_details["response_field_one"]
    response_field_two = agent_details["response_field_two"]
    response_field_three = agent_details["response_field_three"]

    feedback_content_in_bytes = remote_storage.fetch_by_id_iobytes_object(
        first_table_name=first_table_name,
        second_table_name=second_table_name,
        third_tabel_name=third_tabel_name,
        record_id=feedback_id,
        id_column_one=id_column_one,
        id_column_two=id_column_two,
        response_field_one=response_field_one,
        response_field_two=response_field_two,
        response_field_three=response_field_three,
        model=model,
    )
    if feedback_content_in_bytes is None:
        return JSONResponse(
            status_code=404, content={"message": "IEP content not found"}
        )

    pdf_io = generate_pdf_from_markdown(feedback_content_in_bytes, False)

    return Response(
        content=pdf_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={feedback_id}.pdf"},
    )


@feedback_generator_router.get("/download_docx/{feedback_id}")
async def download_feedback_docx(
    feedback_id: str,
    remote_storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    first_table_name = agent_details["table_name_one"]
    second_table_name = agent_details["table_name_two"]
    third_tabel_name = agent_details["table_name_three"]
    id_column_one = agent_details["id_column_one"]
    id_column_two = agent_details["id_column_two"]
    model = agent_details["model"]
    response_field_one = agent_details["response_field_one"]
    response_field_two = agent_details["response_field_two"]
    response_field_three = agent_details["response_field_three"]

    feedack_content_in_bytes_io = remote_storage.fetch_by_id_iobytes_object(
        first_table_name=first_table_name,
        second_table_name=second_table_name,
        third_tabel_name=third_tabel_name,
        record_id=feedback_id,
        id_column_one=id_column_one,
        id_column_two=id_column_two,
        response_field_one=response_field_one,
        response_field_two=response_field_two,
        response_field_three=response_field_three,
        model=model,
    )
    if feedack_content_in_bytes_io is None:
        return JSONResponse(
            status_code=404, content={"message": "Feedback content not found"}
        )

    docx_io = generate_docx_from_markdown(feedack_content_in_bytes_io, False)

    return Response(
        content=docx_io.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={feedback_id}.docx"},
    )


@feedback_generator_router.get("/download_google_doc/{feedback_id}")
async def download_feedback_content_google_doc(
    feedback_id: str,
    remote_storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    first_table_name = agent_details["table_name_one"]
    second_table_name = agent_details["table_name_two"]
    third_tabel_name = agent_details["table_name_three"]
    id_column_one = agent_details["id_column_one"]
    id_column_two = agent_details["id_column_two"]
    model = agent_details["model"]
    response_field_one = agent_details["response_field_one"]
    response_field_two = agent_details["response_field_two"]
    response_field_three = agent_details["response_field_three"]

    feedback_content_in_bytes = remote_storage.fetch_by_id_iobytes_object(
        first_table_name=first_table_name,
        second_table_name=second_table_name,
        third_tabel_name=third_tabel_name,
        record_id=feedback_id,
        id_column_one=id_column_one,
        id_column_two=id_column_two,
        response_field_one=response_field_one,
        response_field_two=response_field_two,
        response_field_three=response_field_three,
        model=model,
    )
    if feedback_content_in_bytes is None:
        return JSONResponse(
            status_code=404, content={"message": "feedback content not found"}
        )

    google_doc_link = generate_google_docs(feedback_content_in_bytes)

    return JSONResponse(content={"google_doc_link": google_doc_link})


@feedback_generator_router.get(path="/interactions_feedback")
async def get_interations(
    request: Request,
    interaction_manager: InteractionManager = Depends(get_interaction_manager),
) -> InteractionResponseFeedback:
    user_id = request.state.user_id
    count = interaction_manager.get_total_interaction_feedback(user_id)
    return InteractionResponseFeedback(
        user_id=user_id, feedback_interaction=count["value"]
    )


@feedback_generator_router.get(path="/edit_input_data")
async def feedback_plan_query_data(
    request: Request, remote_storage: SupabaseStorage = Depends(get_storage)
):
    user_id = request.state.user_id
    feedback_plan_data = remote_storage.fetch_feedback_response_data(user_id=user_id)

    if feedback_plan_data is None:
        return JSONResponse(
            status_code=404,
            content={
                "message": "feedback plan data not found for the given feedback plan id"
            },
        )
    return feedback_plan_data


# This route will retrieve a chat history ID and mark it as favorite in the database
@feedback_generator_router.put("/favorite/{history_id}")
async def favorite_chat_history(
    history_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        success = storage.mark_favorite(history_id, True, "feedback_generator")
        if success:
            return {"message": f"Chat history {history_id} marked as favorite!"}
        else:
            raise HTTPException(status_code=500, detail="Failed to mark as favorite.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# This route will retrieve a chat history ID and mark it as unfavorite in the database
@feedback_generator_router.put("/unfavorite/{history_id}")
async def unfavorite_chat_history(
    history_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        success = storage.mark_favorite(history_id, False, "feedback_generator")
        if success:
            return {"message": f"Chat history {history_id} unmarked as favorite!"}
        else:
            raise HTTPException(status_code=500, detail="Failed to unmark as favorite.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# This route will retrieve all the favourites from a particular user ID
@feedback_generator_router.get("/retrieve_favorites")
async def get_favorite_chats(
    request: Request,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        user_id = request.state.user_id
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        favorite_chats = storage.fetch_favorite_chats(
            user_id, True, "feedback_generator"
        )
        if favorite_chats is not None:
            if len(favorite_chats) == 0:
                return []
            return favorite_chats
        else:
            raise HTTPException(
                status_code=500, detail="Failed to fetch favorite chats."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# Another translation function will translate a particular message id with a requested target language from the front end.
@feedback_generator_router.post("/translate_message/{feedback_id}")
async def translate_message_id(
    feedback_id: str,
    request: TranslationLanguageRequest,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    model = agent_details["model"]
    first_table_name = agent_details["table_name_one"]
    second_table_name = agent_details["table_name_two"]
    third_tabel_name = agent_details["table_name_three"]
    id_column_one = agent_details["id_column_one"]
    id_column_two = agent_details["id_column_two"]
    response_field_one = agent_details["response_field_one"]
    response_field_two = agent_details["response_field_two"]
    response_field_three = agent_details["response_field_three"]
    session_id = agent_details["main_id_reference"]
    refrence_id_one = agent_details["quick_action_main_id_link"]
    refrence_id_two = agent_details["quick_action_chat_id_link"]

    try:
        # Retrieve the chat message from the database using the message_id
        chat_message = storage.fetch_by_id(
            first_table_name,
            second_table_name,
            third_tabel_name,
            feedback_id,
            id_column_one,
            id_column_two,
            response_field_one,
            response_field_two,
            response_field_three,
            session_id,
            refrence_id_one,
            refrence_id_two,
            model,
        )
        if not chat_message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        if "quick_action" in chat_message[0].table_name:
            feedback_id = chat_message[1]
            chat_message[0].table_name = chat_message[2]

        # Translate the text using the AI Coach
        return EventSourceResponse(
            content=agent_class.translate(
                chat_message[0].response,
                chat_message[0].table_name,
                feedback_id,
                request.target_language,
                storage,
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


# Abstracted route to summarize the response as bullet points
@feedback_generator_router.post("/summarize_bulletpoints/{message_id}")
async def summarize_bulletpoints_iep_generator(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response(
        message_id,
        agent_class.summarize_as_bulletpoints,
        agent_class.generate_feedback_generator_id,
        agent_class.get_complete_feedback_response,
        agent_details,
        storage,
    )


# Abstracted route to summarize the response as paragraphs
@feedback_generator_router.post("/summarize_paragraphs/{message_id}")
async def summarize_paragraphs_iep_generator(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response(
        message_id,
        agent_class.summarize_as_paragraphs,
        agent_class.generate_feedback_generator_id,
        agent_class.get_complete_feedback_response,
        agent_details,
        storage,
    )


# Abstracted route to make the message more simple
@feedback_generator_router.post("/make_simpler/{message_id}")
async def make_simpler_iep_generator(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response(
        message_id,
        agent_class.make_simpler,
        agent_class.generate_feedback_generator_id,
        agent_class.get_complete_feedback_response,
        agent_details,
        storage,
    )


# Abstracted route to make the message shorter
@feedback_generator_router.post("/make_shorter/{message_id}")
async def make_shorter_iep_generator(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response(
        message_id,
        agent_class.make_shorter,
        agent_class.generate_feedback_generator_id,
        agent_class.get_complete_feedback_response,
        agent_details,
        storage,
    )


# Abstracted route to make the message longer
@feedback_generator_router.post("/make_longer/{message_id}")
async def make_longer_iep_generator(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response(
        message_id,
        agent_class.make_longer,
        agent_class.generate_feedback_generator_id,
        agent_class.get_complete_feedback_response,
        agent_details,
        storage,
    )


# Abstracted route to make the message more professional
@feedback_generator_router.post("/make_more_professional/{message_id}")
async def make_more_professional_iep_generator(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["feedback_generator"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response(
        message_id,
        agent_class.make_more_professional,
        agent_class.generate_feedback_generator_id,
        agent_class.get_complete_feedback_response,
        agent_details,
        storage,
    )


@feedback_generator_router.websocket("/chat")
async def chat_with_feedback_coach(
    socket: WebSocket,
    contextId: str | None = Query(default=None),
    chat_id: str | None = Query(default=None),
    user: str = Depends(get_or_verify_token),
    chat_manager: ChatManager = Depends(get_chat_manager),
):
    user_id = user.get("user_id")
    if not user_id:
        await socket.close(
            code=1008
        )  # Close WebSocket connection with policy violation code
        return

    await socket.accept()
    try:
        feedback_chat = Feedbackchat()
        agent_details = AGENT_DETAILS["feedback_generator"]

        processor = chat_manager.get_chat_processor(user_id)
        if processor is None:
            print(f"creating new processor for {user_id}")
            processor = ChatProcessor(
                socket=socket,
                feedback_chat=feedback_chat,
                history_id=contextId,
                token=user.get("token"),
                agent_details=agent_details,
                chat_id=chat_id,
            )
            chat_manager.add_chat_processor(user_id, processor)
        try:
            await processor.start()
        finally:
            chat_manager.remove_chat_processor(
                user_id
            )  # Clean up when the connection is closed
            print(f"Connection closed for {user_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Response: {e}")
