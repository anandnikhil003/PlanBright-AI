import os
import asyncio
from typing import Dict, Optional, Any
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, WebSocket, HTTPException, Request, Query
from agents.ai_coach import AICoach
from models.data_models import InteractionResponseAiCoach
from models.data_models import PDFQuery
from models.data_models import TranslationLanguageRequest
from data_ingestion.ingestion_pipline import process_pdf
from db.remote_storage import SupabaseStorage, get_storage
from db.interaction_manager import InteractionManager, get_interaction_manager
from models.data_models import FeedbackData, EditQuery
from security.auth import get_or_verify_token, update_activity
from config.utils import (
    process_and_save_response_for_aicoach,
)
from config.agent_details import AGENT_DETAILS
from fastapi.responses import JSONResponse, Response
from config.utils import (
    generate_pdf_from_markdown,
    generate_docx_from_markdown,
    generate_google_docs,
)


load_dotenv()

coach_router = APIRouter(prefix="/api/ai_coach", tags=["Interactive Chat"])

# TODO - link a school -> user -> session for chat history and retreival
#        as of now conversations are stored per user basis
# TODO - create api to fetch the history session wise
# TODO - store Example(id,query,response,feedback) in the backend for metrics
# TODO - store prompts in database
# TODO - create api to update the prompts
# TODO - create api to fetch the prompts


class ChatProcessor:
    """
    Processor to process each conversation
    """

    query_engine: Optional[Any] = None  # Class-level variable to store the query_engine

    def __init__(
        self,
        socket: WebSocket,
        ai_coach: AICoach,
        user_id: str,
        history_id: str,
        interaction_manager: InteractionManager,
        token: str,
        chat_id: Optional[str] = None,
        query_engine: Optional[Any] = None,
    ):
        self.socket = socket
        self.coach = ai_coach
        self.user_id = user_id
        self.history_id = history_id
        self.query_engine = query_engine
        self.token = token
        self.interaction_manager = interaction_manager
        self.chat_id = chat_id

    async def process(self):
        print("preparing to send responses")
        try:
            while True:
                msg = await self.coach.response_queue.get()
                await self.socket.send_text(msg)
                self.coach.response_queue.task_done()
        except asyncio.CancelledError:
            print("Processing task was cancelled")

    async def start(self, endpoint_name: str):
        processing_task = asyncio.create_task(self.process())
        try:
            while True:
                msg = await self.socket.receive_text()
                # if msg == "abort_response":
                #     self.coach.abort_event.set()  # Signal to abort
                if msg == "reopen_new_chat":
                    # Create a history_id for the current user session
                    self.history_id = self.coach.generate_chat_id()

                elif endpoint_name == "document_chat":
                    self.interaction_manager.add_interaction_Ai_Coach(
                        user_id=self.user_id
                    )
                    await self.coach.chat_with_document(
                        query=msg, query_engine=ChatProcessor.query_engine
                    )
                else:
                    self.interaction_manager.add_interaction_Ai_Coach(
                        user_id=self.user_id
                    )
                    asyncio.create_task(update_activity(self.token))
                    await self.coach.chat(
                        query=msg,
                        history_id=self.history_id,
                        user_id=self.user_id,
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


@coach_router.get(path="/interactions")
async def get_interations(
    request: Request,
    interaction_manager: InteractionManager = Depends(get_interaction_manager),
) -> InteractionResponseAiCoach:
    user_id = request.state.user_id
    count = interaction_manager.get_total_interactions_Ai_Coach(user_id)
    return InteractionResponseAiCoach(user_id=user_id, bot_interaction=count["value"])


@coach_router.get("/history")
async def get_chat_history_user(
    request: Request,
    storage: SupabaseStorage = Depends(get_storage),
):
    user_id = request.state.user_id
    try:
        # Fetch chat history for the given user_id
        chat_history = storage.fetch_cleaned_data(user_id)

        if chat_history:
            return chat_history
        else:
            return []
    except Exception as e:
        print("The error is:", str(e))


@coach_router.get("/history_list/{history_id}")
async def get_chat_history(
    history_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        chat_history = storage.get_chat_history_list(history_id)

        # Return the chat history
        return chat_history
    except Exception as e:
        print("The error is:", str(e))


@coach_router.put("/update_feedback/{chat_msg_id}")
async def add_feedback(
    chat_msg_id: str,
    feedback: FeedbackData,
    storage: SupabaseStorage = Depends(get_storage),
):
    udpdated_response = storage.update_feedback_intreactive_chat(
        chat_msg_id, feedback.feedback, feedback.feedback_description
    )
    if udpdated_response is None:
        return {"message": "Feedback updated successfully!"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to update feedback as no chat message ID: {chat_msg_id} exist",
        )


@coach_router.put("/edit_query/{history_id}")
async def edit_user_query(
    history_id: str,
    edited_msg: EditQuery,
    storage: SupabaseStorage = Depends(get_storage),
):
    edited_response = storage.setup_to_edit(history_id, edited_msg.edited_query)

    if edited_response:
        return {"message": "Edited user query successfully!"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to edit usery query as no chat history ID: {history_id} exist",
        )


@coach_router.get("/download_pdf/{chat_msg_id}")
async def download_interactivechat_content_pdf(
    chat_msg_id: str,
    remote_storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["ai_coach_msg"]
    model = agent_details["model"]
    first_table_name = agent_details["table_name_one"]
    second_table_name = agent_details["table_name_two"]
    id_column_one = agent_details["id_column_one"]
    id_column_two = agent_details["id_column_two"]
    response_field_one = agent_details["response_field_one"]
    response_field_two = agent_details["response_field_two"]
    chat_content_in_bytes_io = remote_storage.get_interactivechat_by_id_iobytes_object(
        first_table_name=first_table_name,
        second_table_name=second_table_name,
        record_id=chat_msg_id,
        id_column_one=id_column_one,
        id_column_two=id_column_two,
        response_field_one=response_field_one,
        response_field_two=response_field_two,
        model=model,
    )
    if chat_content_in_bytes_io is None:
        return JSONResponse(
            status_code=404, content={"message": "Assesment content not found"}
        )

    pdf_io = generate_pdf_from_markdown(chat_content_in_bytes_io, False)

    return Response(
        content=pdf_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={chat_msg_id}.pdf"},
    )


@coach_router.get("/download_docx/{chat_msg_id}")
async def download_interactivechat_docx(
    chat_msg_id: str,
    remote_storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["ai_coach_msg"]
    model = agent_details["model"]
    first_table_name = agent_details["table_name_one"]
    second_table_name = agent_details["table_name_two"]
    id_column_one = agent_details["id_column_one"]
    id_column_two = agent_details["id_column_two"]
    response_field_one = agent_details["response_field_one"]
    response_field_two = agent_details["response_field_two"]
    chat_content_in_bytes_io = remote_storage.get_interactivechat_by_id_iobytes_object(
        first_table_name=first_table_name,
        second_table_name=second_table_name,
        record_id=chat_msg_id,
        id_column_one=id_column_one,
        id_column_two=id_column_two,
        response_field_one=response_field_one,
        response_field_two=response_field_two,
        model=model,
    )
    if chat_content_in_bytes_io is None:
        return JSONResponse(
            status_code=404, content={"message": "Assesment content not found"}
        )

    docx_io = generate_docx_from_markdown(chat_content_in_bytes_io, False)

    return Response(
        content=docx_io.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={chat_msg_id}.docx"},
    )


@coach_router.get("/download_google_doc/{chat_msg_id}")
async def download_interactivechat_google_doc(
    chat_msg_id: str,
    remote_storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["ai_coach_msg"]
    model = agent_details["model"]
    first_table_name = agent_details["table_name_one"]
    second_table_name = agent_details["table_name_two"]
    id_column_one = agent_details["id_column_one"]
    id_column_two = agent_details["id_column_two"]
    response_field_one = agent_details["response_field_one"]
    response_field_two = agent_details["response_field_two"]
    chat_content_in_bytes_io = remote_storage.get_interactivechat_by_id_iobytes_object(
        first_table_name=first_table_name,
        second_table_name=second_table_name,
        record_id=chat_msg_id,
        id_column_one=id_column_one,
        id_column_two=id_column_two,
        response_field_one=response_field_one,
        response_field_two=response_field_two,
        model=model,
    )
    if chat_content_in_bytes_io is None:
        return JSONResponse(
            status_code=404, content={"message": "Chat content not found"}
        )

    google_doc_link = generate_google_docs(chat_content_in_bytes_io)

    return JSONResponse(content={"google_doc_link": google_doc_link})


@coach_router.delete("/delete_history/{history_id}")
async def delete_history(
    history_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    delete_response = storage.delete_history_intreactive_chat(history_id)
    if delete_response is None:
        return {"message": "history deleted successfully!"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to delete as no chat message ID: {history_id} exist",
        )


# Added a clear all button which should clear all the chats from a specific user ID
@coach_router.delete("/clear_all_history")
async def clear_all_history(
    request: Request,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        user_id = request.state.user_id
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        response = storage.delete_all_history_for_user(user_id)
        if response.get("message") == "No chat history found for the user.":
            return {"message": "No chat history found for the user."}
        elif response.get("message") == "All chat history deleted successfully!":
            return {"message": "All chat history deleted successfully!"}
        else:
            raise HTTPException(status_code=500, detail=response.get("message"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# This route will retrieve a chat history ID and mark it as favorite in the database
@coach_router.put("/favorite/{id}")
async def favorite_chat_history(
    id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        success = storage.mark_favorite(id, True, "ai_coach_msg")
        if success:
            return {"message": f"Chat history {id} marked as favorite!"}
        else:
            raise HTTPException(status_code=500, detail="Failed to mark as favorite.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# This route will retrieve a chat history ID and mark it as unfavorite in the database
@coach_router.put("/unfavorite/{id}")
async def unfavorite_chat_history(
    id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        success = storage.mark_favorite(id, False, "ai_coach_msg")
        if success:
            return {"message": f"Chat history {id} unmarked as favorite!"}
        else:
            raise HTTPException(status_code=500, detail="Failed to unmark as favorite.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# This route will retrieve all the favourites from a particular user ID
@coach_router.get("/retrieve_favorites")
async def get_favorite_chats(
    request: Request,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        user_id = request.state.user_id

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        favorite_chats = storage.fetch_favorite_chats(user_id, True, "ai_coach_history")
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
@coach_router.post("/translate_message/{message_id}")
async def translate_message_id(
    message_id: str,
    request: TranslationLanguageRequest,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["ai_coach_msg"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    model = agent_details["model"]
    first_table_name = agent_details["table_name_one"]
    second_table_name = agent_details["table_name_two"]
    id_column_one = agent_details["id_column_one"]
    id_column_two = agent_details["id_column_two"]
    response_field_one = agent_details["response_field_one"]
    response_field_two = agent_details["response_field_two"]
    session_id = agent_details["session_id"]
    refrence_id = agent_details["refrence_id"]

    try:
        # Retrieve the chat message from the database using the message_id
        chat_message, required_id = storage.fetch_by_id_for_aicoach(
            first_table_name=first_table_name,
            second_table_name=second_table_name,
            record_id=message_id,
            id_column_one=id_column_one,
            id_column_two=id_column_two,
            response_field_one=response_field_one,
            response_field_two=response_field_two,
            session_id=session_id,
            refrence_id=refrence_id,
            model=model,
        )
        # Check if 'quick_action' is in the table name
        if "quick_action" in chat_message.table_name:
            message_id = required_id

        if not chat_message:
            raise HTTPException(status_code=404, detail="Chat message not found")

        # Translate the text using the AI Coach
        return EventSourceResponse(
            content=agent_class.translate(
                chat_message.response,
                chat_message.table_name,
                message_id,
                request.target_language,
                storage,
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


# Abstracted route to summarize the response as bullet points
@coach_router.post("/summarize_bulletpoints/{message_id}")
async def summarize_bulletpoints_ai_coach(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["ai_coach_msg"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response_for_aicoach(
        message_id,
        agent_class.summarize_as_bulletpoints,
        agent_class.generate_chat_id,
        agent_class.get_complete_response,
        agent_details,
        storage,
    )


# Abstracted route to summarize the response as paragraphs
@coach_router.post("/summarize_paragraphs/{message_id}")
async def summarize_paragraphs_ai_coach(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["ai_coach_msg"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response_for_aicoach(
        message_id,
        agent_class.summarize_as_paragraphs,
        agent_class.generate_chat_id,
        agent_class.get_complete_response,
        agent_details,
        storage,
    )


# Abstracted route to make the message more simple
@coach_router.post("/make_simpler/{message_id}")
async def make_simpler_ai_coach(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["ai_coach_msg"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response_for_aicoach(
        message_id,
        agent_class.make_simpler,
        agent_class.generate_chat_id,
        agent_class.get_complete_response,
        agent_details,
        storage,
    )


# Abstracted route to make the message shorter
@coach_router.post("/make_shorter/{message_id}")
async def make_shorter_ai_coach(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["ai_coach_msg"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response_for_aicoach(
        message_id,
        agent_class.make_shorter,
        agent_class.generate_chat_id,
        agent_class.get_complete_response,
        agent_details,
        storage,
    )


# Abstracted route to make the message longer
@coach_router.post("/make_longer/{message_id}")
async def make_longer_ai_coach(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["ai_coach_msg"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response_for_aicoach(
        message_id,
        agent_class.make_longer,
        agent_class.generate_chat_id,
        agent_class.get_complete_response,
        agent_details,
        storage,
    )


# Abstracted route to make the message more professional
@coach_router.post("/make_more_professional/{message_id}")
async def make_more_professional_ai_coach(
    message_id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    agent_details = AGENT_DETAILS["ai_coach_msg"]
    agent_class = agent_details["class"](**agent_details["init_args"])
    return await process_and_save_response_for_aicoach(
        message_id,
        agent_class.make_more_professional,
        agent_class.generate_chat_id,
        agent_class.get_complete_response,
        agent_details,
        storage,
    )


@coach_router.post("/process_pdf/")
async def process_pdf_endpoint(pdf_query: PDFQuery = Depends()):
    try:
        base_directory = os.getenv("UC_BOT_DATA_DIRECTORY")
        document_type = pdf_query.document_type
        document_directory = f"data_ingestion/pdf_data/{document_type}-doc"
        os.makedirs(document_directory, exist_ok=True)

        # Save the uploaded file to the corresponding directory
        file_path = f"{document_directory}/{pdf_query.file.filename}"
        with open(file_path, "wb") as f:
            f.write(pdf_query.file.file.read())

        # Create the final_file_path by combining base_directory and file_path
        final_file_path = os.path.join(base_directory, file_path)

        # Use the process_pdf function to create the query engine
        ChatProcessor.query_engine = process_pdf(final_file_path)

        # Additional logic to process the PDF if needed

        return {
            "message": "PDF processed successfully!",
            "query_engine": "Query engine created",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@coach_router.websocket("/chat")
async def chat_with_coach(
    socket: WebSocket,
    history_id: str | None = Query(default=None),
    chat_id: str | None = Query(default=None),
    user: str = Depends(get_or_verify_token),
    chat_manager: ChatManager = Depends(get_chat_manager),
    interaction_manager: InteractionManager = Depends(get_interaction_manager),
):
    user_id = user.get("user_id")
    if not user_id:
        await socket.close(
            code=1008
        )  # Close WebSocket connection with policy violation code
        return

    await socket.accept()
    try:
        ai_coach = AICoach(
            model=os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o"), apiKey=os.getenv("AZURE_API_KEY")
        )
        if history_id is None:
            # Create a history_id for the current user session
            history_id = ai_coach.generate_chat_id()

        processor = chat_manager.get_chat_processor(user_id)
        if processor is None:
            print(f"creating new processor for {user_id}")
            processor = ChatProcessor(
                socket=socket,
                ai_coach=ai_coach,
                user_id=user_id,
                history_id=history_id,
                interaction_manager=interaction_manager,
                token=user.get("token"),
                chat_id=chat_id,
            )
            chat_manager.add_chat_processor(user_id, processor)
        try:
            await processor.start(endpoint_name="chat")
        finally:
            chat_manager.remove_chat_processor(
                user_id
            )  # Clean up when the connection is closed
            print(f"Connection closed for {user_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Response: {e}")


@coach_router.websocket("/document_chat")
async def document_chat_with_coach(
    socket: WebSocket,
    user_id: str = Depends(get_or_verify_token),
    chat_manager: ChatManager = Depends(get_chat_manager),
    interaction_manager: InteractionManager = Depends(get_interaction_manager),
    storage: SupabaseStorage = Depends(get_storage),
):
    await socket.accept()

    ai_coach = AICoach()
    # Create a history_id for the current user session
    history_id = ai_coach.generate_chat_id()

    # Add chat history to the database
    storage.add_chat_history(history_id=history_id, user_id=user_id)

    processor = chat_manager.get_chat_processor(user_id)

    if processor is None:
        print(f"creating new processor for {user_id}")
        processor = ChatProcessor(
            socket=socket,
            ai_coach=ai_coach,
            history_id=history_id,
            interaction_manager=interaction_manager,
        )
        chat_manager.add_chat_processor(user_id, processor, interaction_manager)

    try:
        await processor.start(endpoint_name="document_chat")
    finally:
        chat_manager.remove_chat_processor(user_id)
        print(f"Connection closed for {user_id}")
