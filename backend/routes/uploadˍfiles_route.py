from fastapi import File, UploadFile, HTTPException, APIRouter
import pymupdf4llm
import tempfile
import mammoth
import markdownify
import os
from config.utils import clean_and_join_text
from models.data_models import ExtractedPdfContent, ExtractedDocxContent

upload_file_router = APIRouter(prefix="/api/upload_files", tags=["Upload File API"])


@upload_file_router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)) -> ExtractedPdfContent:
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        md_text = pymupdf4llm.to_markdown(tmp_path)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error converting PDF to Markdown: {str(e)}"
        )
    finally:
        # Clean up the temporary file
        os.remove(tmp_path)

    cleaned_text = clean_and_join_text(md_text)
    return ExtractedPdfContent(extracted_content=cleaned_text)


@upload_file_router.post("/upload-docx/")
async def upload_docx(file: UploadFile = File(...)) -> ExtractedDocxContent:
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only DOCX files are allowed")

    try:
        # Create a temporary file to store the uploaded DOCX
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Convert DOCX to HTML using mammoth
        with open(tmp_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value  # The generated HTML

        # Convert HTML to Markdown using markdownify
        md_text = markdownify.markdownify(html, heading_style="ATX")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="The file is not readable. Please try again!"
        )
        print(f"Error converting DOCX to Markdown: {str(e)}")
    finally:
        # Clean up the temporary file
        os.remove(tmp_path)

    cleaned_text = clean_and_join_text(md_text)
    return ExtractedDocxContent(extracted_content=cleaned_text)
