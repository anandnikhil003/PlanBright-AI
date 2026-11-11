import os
from typing import List
from typing import Tuple
import boto3
import docx2txt
import dotenv
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException
from fastapi import UploadFile
from langchain_community.document_loaders import TextLoader
from llama_parse import LlamaParse
from config.azure_provider import azure_openai_client, azure_embedding_deployment
from bot.database.manager import DatabaseManager
from bot.database.schemas.bot_file import BotFileCreate
from bot.database.schemas.bot_file import ExtractedFile
import uuid

dotenv.load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
ENDPOINT_URL = os.getenv("ENDPOINT_URL")
REGION_NAME = os.getenv("REGION_NAME")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME,
)


class Document:
    count = 0

    def __init__(self, doc):
        self.id_ = doc.id_
        self.metadata = doc.metadata
        self.page_content = doc.text
        self.page = Document.count
        Document.count += 1


class docx_Document:
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content  # The main text/content of the document
        self.metadata = metadata  # Metadata like source, author, date, etc.


class BotFileCRUD:
    def __init__(self):
        self.db = DatabaseManager().get_client()

    def create_bot_file(self, bot_file_data: BotFileCreate):
        try:
            result = self.db.table("BotFiles").insert(bot_file_data.dict()).execute()
            # Assuming result.data contains a list, extract the first item
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to create school: No data returned"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create bot file: {e}"
            )

    def get_bot_file(self, file_id: str):
        try:
            result = (
                self.db.table("BotFiles")
                .select("*")
                .eq("id", file_id)
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Bot file not found")
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve bot file: {e}"
            )

    def get_bot_files(self, bot_id: str):
        try:
            result = (
                self.db.table("BotFiles").select("*").eq("bot_id", bot_id).execute()
            )
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve bot files: {e}"
            )

    def update_bot_file(self, file_id: str, bot_file_data: BotFileCreate):
        try:
            result = (
                self.db.table("BotFiles")
                .update(bot_file_data.dict())
                .eq("id", file_id)
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
                status_code=500, detail=f"Failed to update bot file: {e}"
            )

    def delete_bot_file(self, file_id: str):
        try:
            self.db.table("BotFiles").delete().eq("id", file_id).execute()
            return {"message": "Bot file deleted"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete bot file: {e}"
            )

    # def extract_text_from_file(self, file_path) -> ExtractedFile:
    #     # Check if file exists
    #     if not os.path.exists(file_path):
    #         error_message = f"Error: File not found: {file_path}"
    #         return {"error": error_message}

    #     file_extension = os.path.splitext(file_path)[1].lower()
    #     print(
    #         f"Starting text extraction from {file_path} with extension {file_extension}"
    #     )

    #     try:
    #         if file_extension == ".docx":
    #             page_content = docx2txt.process(file_path)
    #             document_obj = docx_Document(
    #                 page_content=page_content, metadata={"source": file_path}
    #             )
    #             return ExtractedFile(
    #                 extracted_content=[document_obj], meta_data=file_path
    #             )
    #         elif file_extension == ".pdf":
    #             llama_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    #             parser = LlamaParse(
    #                 api_key=llama_api_key,
    #                 result_type="markdown",  # "markdown" and "text" are available
    #                 num_workers=2,  # if multiple files passed, split in `num_workers` API calls
    #                 verbose=True,
    #                 language="en",  # Optionally you can define a language, default=en
    #             )
    #             documents = parser.load_data(file_path)
    #             modified_docs = [Document(doc) for doc in documents]
    #             print("modified_docs : ", len(modified_docs))
    #             return ExtractedFile(
    #                 extracted_content=modified_docs, meta_data=file_path
    #             )

    #         elif file_extension == ".txt":
    #             loader = TextLoader(file_path, encoding="utf-8")
    #             document = loader.load()
    #             modified_docs = [Document(doc) for doc in document]
    #             return ExtractedFile(
    #                 extracted_content=modified_docs,
    #                 meta_data=document[0].metadata["source"],
    #             )
    #         else:
    #             raise ValueError("Unsupported file format")

    #     except Exception as e:
    #         error_message = (
    #             f"An error occurred while extracting text from {file_path}: {e}"
    #         )
    #         print(error_message)
    #         return {"error": error_message}

    # # Function to preprocess and generate embeddings
    # def generate_embeddings_from_file(
    #     self,
    #     file_path: str,
    # ) -> Tuple[List[List[float]], bool]:
    #     id = self.generate_bot_file_id()
    #     print(f"generating bot embeddings with id {id}")
    #     client = azure_openai_client()
    #     contents = self.extract_text_from_file(file_path)
    #     texts = []

    #     for item in contents.extracted_content:
    #         # Append the page_content of each item to the texts list
    #         texts.append(item.page_content)

    #     print("generated text len: ", len(texts))
    #     print("each generated text len: ", len(texts[0]))
    #     try:
    #         response = client.embeddings.create(
    #             input=texts, model=azure_embedding_deployment(), encoding_format="float"
    #         )
    #         # Extract the embedding vector
    #         embeddings = response.data[0].embedding
    #     except Exception as e:
    #         print(f"Error generating embeddings: {e}")
    #         return [], False

    #     data = {
    #         "id": id,
    #         "content_type": os.path.basename(file_path),  # Store the file name
    #         "content": {"text": texts},  # Store the entire extracted text as JSON
    #         "embedding_id": None,  # Set embedding_id to null
    #         "embedding": embeddings,  # Store all embeddings as a single array
    #         "meta": {},  # Optional metadata
    #     }

    #     try:
    #         # Insert the data into Supabase as a single row
    #         self.db.table("BotFiles").insert(data).execute()
    #     except Exception as e:
    #         print("error in bot creation ", e)
    #         return embeddings, False
    #     return (embeddings, True, id)

    # Function to upload file to S3
    def upload_to_s3(self, file: UploadFile, bucket_name: str, file_key: str) -> str:
        try:
            s3_client.upload_fileobj(file, bucket_name, file_key)
            return f"s3://{bucket_name}/{file_key}"
        except NoCredentialsError:
            raise HTTPException(status_code=403, detail="S3 credentials are invalid.")

    def bot_embedding_information(self, bot_id: str):
        try:
            response = (
                self.db.table("BotFiles2").select("id").eq("bot_id", bot_id).execute()
            )
            data_info = response.data
            return data_info
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch bot file embeddings: {e}"
            )

    def search_relevant_embedding(self, query_embedding, bot_id):
        try:
            result = self.db.rpc(
                "get_top_similar_embeddings",
                {"query_embedding": f"{query_embedding}", "input_bot_id": bot_id},
            ).execute()
            embedding_info = result.data
            return embedding_info
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch relevant embeddings: {e}"
            )

    def generate_bot_file_id(self) -> str:
        return str(uuid.uuid4())

    def generate_embeddings_from_all_file(
        self,
        file_path: str,
    ) -> Tuple[List[List[float]], bool]:
        # Check if file exists
        if not os.path.exists(file_path):
            error_message = f"Error: File not found: {file_path}"
            return {"error": error_message}

        file_extension = os.path.splitext(file_path)[1].lower()
        print(
            f"Starting text extraction from {file_path} with extension {file_extension}"
        )
        id = self.generate_bot_file_id()
        print(f"generating bot embeddings with id {id}")
        session_data = {
            "id": id,
            "file_name": os.path.basename(file_path),
            "file_type": file_extension,
        }
        try:
            # Insert the data into Supabase as a single row
            self.db.table("BotFiles2").insert(session_data).execute()
        except Exception as e:
            print("error in bot creation ", e)
        llama_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        parser = LlamaParse(
            api_key=llama_api_key,
            result_type="markdown",  # "markdown" and "text" are available
            num_workers=9,  # if multiple files passed, split in `num_workers` API calls
            verbose=True,
            language="en",
            skip_diagonal_text=True,
            do_not_unroll_columns=True,
            split_by_page=True,
            check_interval=1,  # Optionally you can define a language, default=en
        )
        client = azure_openai_client()
        document = parser.load_data(file_path=file_path)
        print("length of document ------", len(document))
        for doc in range(len(document)):
            embed_id = self.generate_bot_file_id()
            text = document[doc].text
            try:
                response = client.embeddings.create(
                    input=text, model=azure_embedding_deployment(), encoding_format="float"
                )
                # Extract the embedding vector
                embeddings = response.data[0].embedding
            except Exception as e:
                print(f"Error generating embeddings: {e}")
                return [], False
            embedding_data = {
                "id": embed_id,
                "text_content": text,
                "file_id": id,
                "embedding": embeddings,
            }
            try:
                # Insert the data into Supabase as a single row
                self.db.table("Embeddings").insert(embedding_data).execute()
            except Exception as e:
                print("error in bot creation ", e)
                return embeddings, False
        return (embeddings, True, id)
