import os
from io import BytesIO
from pathlib import Path

# import nest_asyncio
from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile

from bot.database.crud.bot_file import BotFileCRUD
from bot.database.crud.embedding import EmbeddingCRUD
from bot.database.schemas.bot_file import BotFile
from bot.database.schemas.bot_file import BotFileCreate

# nest_asyncio.apply()

bots_files = APIRouter(prefix="/api/bots_files", tags=["Bots_Files"])


def get_bot_file_crud():
    return BotFileCRUD()


def get_embedding_crud():
    return EmbeddingCRUD


@bots_files.post("/bots/{bot_id}/files", response_model=BotFile)
async def create_bot_file(
    bot_id: str,
    bot_file: BotFileCreate,
    bot_file_crud: BotFileCRUD = Depends(get_bot_file_crud),
):
    bot_file.bot_id = bot_id  # Set the bot_id from the URL parameter
    return bot_file_crud.create_bot_file(bot_file)


@bots_files.get("/bots/{bot_id}/files", response_model=list[BotFile])
async def list_bot_files(
    bot_id: str, bot_file_crud: BotFileCRUD = Depends(get_bot_file_crud)
):
    return bot_file_crud.get_bot_files(bot_id)


@bots_files.get("/bots/{bot_id}/files/{file_id}", response_model=BotFile)
async def read_bot_file(
    file_id: str, bot_file_crud: BotFileCRUD = Depends(get_bot_file_crud)
):
    return bot_file_crud.get_bot_file(file_id)


@bots_files.put("/bots/{bot_id}/files/{file_id}", response_model=BotFile)
async def update_bot_file(
    file_id: str,
    bot_file: BotFileCreate,
    bot_file_crud: BotFileCRUD = Depends(get_bot_file_crud),
):
    return bot_file_crud.update_bot_file(file_id, bot_file)


@bots_files.delete("/bots/{bot_id}/files/{file_id}")
async def delete_bot_file(
    file_id: str, bot_file_crud: BotFileCRUD = Depends(get_bot_file_crud)
):
    return bot_file_crud.delete_bot_file(file_id)


@bots_files.post("/bots/{bot_id}/upload_pdf")
async def upload_pdf_and_create_embedding(
    bot_id: str,
    file: UploadFile = File(...),
    bot_file_crud: BotFileCRUD = Depends(get_bot_file_crud),
    embedding_crud: EmbeddingCRUD = Depends(get_embedding_crud),
):
    # Step 1: Validate the file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")


# new code is added
@bots_files.post("/upload_and_extract")
async def upload_and_extract(
    request: Request,
    file: UploadFile = File(...),
    bot_file_crud: BotFileCRUD = Depends(get_bot_file_crud),
):
    user_id = request.state.user_id
    file_key = f"bot-files/{user_id}/{file.filename}"
    s3_path = None  # Initialize s3_path to None
    tmp_path = None  # Initialize tmp_path to None
    try:
        # Upload file to S3
        file_content = await file.read()
        # Upload file to S3 using a BytesIO copy of the content
        s3_file = BytesIO(file_content)
        s3_path = bot_file_crud.upload_to_s3(
            s3_file, os.getenv("AWS_BUCKET_NAME"), file_key
        )
    except Exception as e:
        print(f"Failed to upload file to S3: {e}")
        # raise HTTPException(status_code=500, detail="Failed to upload file to S3")
    bin_folder = Path("bin")  # Change to your actual bin folder path
    bin_folder.mkdir(parents=True, exist_ok=True)  # Ensure bin directory exists
    bin_file_path = bin_folder / file.filename
    try:
        with open(bin_file_path, "wb") as bin_file:
            bin_file.write(file_content)

            # Check if file was written and path exists for debugging purposes
        if not bin_file_path.exists():
            print("File was not saved in bin folder.")
            raise HTTPException(
                status_code=500, detail="Failed to save file in bin folder."
            )

        # Call `generate_embeddings_from_file` with the temp_path
        embeddings, success, bot_embedding_id = (
            bot_file_crud.generate_embeddings_from_all_file(str(bin_file_path))
        )

    except Exception as e:
        print(f"Failed to generate embeddings: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate embeddings")

    finally:
        # Ensure the temporary file is deleted if it was created
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    if not success:
        raise HTTPException(
            status_code=500, detail="Embedding generation returned no results"
        )

    return {
        "message": "File uploaded and processed successfully.",
        "bot_embedding_id": bot_embedding_id,
        "s3_path": s3_path,
        "embeddings": "embeddings created",
    }
