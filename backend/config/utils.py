import markdown2
from sse_starlette.sse import EventSourceResponse
import io
import tempfile
import re
import os
import threading
from db.remote_storage import SupabaseStorage
from fastapi import HTTPException
from pdf2docx import Converter
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import time

# Path to the service account key file
SERVICE_ACCOUNT_FILE = "uc_googleapi_dev_credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


def generate_pdf_from_markdown(content_bytes_io, google_docs_boolean):
    # WeasyPrint loads native GTK libraries on Windows; defer that requirement until PDF export.
    from weasyprint import HTML, CSS

    content_markdown = content_bytes_io.getvalue().decode("utf-8")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_file_relative = os.path.join(current_dir, "style.css")

    # Relative path to the header image
    header_image_path = os.path.join(current_dir, "../unconstrained_logo.png")

    # Convert markdown to HTML
    content_html = markdown2.markdown(
        content_markdown, extras=["tables", "fenced-code-blocks"]
    )

    # If we're converting from pdf to google docs, don't include the logo as that will be done manually
    if google_docs_boolean:
        final_html_content = f"""
        <html>
        <head>
            <link rel="stylesheet" href="file:///{css_file_relative}">
        </head>
        <body>
            <main>
                {content_html}
            </main>
        </body>
        </html>
        """

    else:
        # Add header and logo in HTML
        final_html_content = f"""
        <html>
        <head>
            <link rel="stylesheet" href="file:///{css_file_relative}">
        </head>
        <body>
            <header>
                <div class="header-content">
                    <img src="file:///{header_image_path}" style="max-width: 100%;" />
                </div>
            </header>
            <main>
                {content_html}
            </main>
        </body>
        </html>
        """

    pdf_io = io.BytesIO()
    # Convert HTML to PDF with CSS

    HTML(string=final_html_content).write_pdf(
        pdf_io, stylesheets=[CSS(filename=css_file_relative)]
    )
    pdf_io.seek(0)
    return pdf_io


def generate_docx_from_markdown(content_bytes_io, google_docs_boolean):
    # Generate PDF from markdown
    pdf_io = generate_pdf_from_markdown(content_bytes_io, google_docs_boolean)

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
        temp_pdf_file.write(pdf_io.getvalue())
        temp_pdf_filename = temp_pdf_file.name

    temp_docx_filename = temp_pdf_filename.replace(".pdf", ".docx")

    try:
        # Convert PDF to DOCX
        cv = Converter(temp_pdf_filename)
        cv.convert(temp_docx_filename, start=0, end=None)
        cv.close()
    except AttributeError as e:
        print(f"Error during conversion: {e}")
        return None

    # Read the DOCX file back into a BytesIO object
    with open(temp_docx_filename, "rb") as file:
        docx_io = io.BytesIO(file.read())

    # Clean up temporary files
    os.remove(temp_pdf_filename)
    os.remove(temp_docx_filename)

    return docx_io


# Google Docs Functionality ======================================================================================================
# Used to connect to the Google Cloud Console
def authenticate_google_services():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)
    return drive_service, docs_service


def upload_image_to_drive(image_path):
    drive_service, _ = authenticate_google_services()

    file_metadata = {"name": os.path.basename(image_path), "mimeType": "image/png"}
    media = MediaFileUpload(image_path, mimetype="image/png")
    file = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    # Get the file ID and make it accessible via a public link
    file_id = file.get("id")
    drive_service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()

    file_url = f"https://drive.google.com/uc?export=view&id={file_id}"
    print(file_url)
    return file_url


# current_dir = os.path.dirname(os.path.abspath(__file__))
# header_image_path = os.path.join(current_dir, "../unconstrained_logo.png")
# BRANDING_IMAGE_URL = upload_image_to_drive(header_image_path)
BRANDING_IMAGE_URL = (
    "https://drive.google.com/uc?export=view&id=16l4S5Tm5UCjWQ_wWT5dAhW3Z3SjKjEyu"
)


def create_empty_google_doc(document_title):
    drive_service, _ = authenticate_google_services()
    doc_metadata = {
        "name": document_title,
        "mimeType": "application/vnd.google-apps.document",
    }

    doc = drive_service.files().create(body=doc_metadata).execute()
    doc_id = doc["id"]

    # Set permissions to allow user to view and edit immediately
    permission_body = {"type": "anyone", "role": "writer"}
    drive_service.permissions().create(fileId=doc_id, body=permission_body).execute()

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_id, doc_url


# Clean markdown styling and capture style requests
def clean_and_capture_styles(chunk, index):
    requests = []
    bolditalics_match = re.search(r"\*\*\*(.+?)\*\*\*", chunk)
    bold_match = re.search(r"\*\*(.+?)\*\*", chunk)
    italic_match = re.search(r"\*(.+?)\*", chunk)
    underline_match = re.search(r"\_(.+?)\_", chunk)

    if bolditalics_match:
        text = bolditalics_match.group(1).strip()
        requests.append(get_text_style_request(text, "bold", index))
        requests.append(get_text_style_request(text, "italic", index))
        chunk = re.sub(r"\*\*\*(.+?)\*\*\*", text, chunk)

    elif bold_match:
        text = bold_match.group(1).strip()
        requests.append(get_text_style_request(text, "bold", index))
        chunk = re.sub(r"\*\*(.+?)\*\*", text, chunk)

    elif italic_match:
        text = italic_match.group(1).strip()
        requests.append(get_text_style_request(text, "italic", index))
        chunk = re.sub(r"\*(.+?)\*", text, chunk)

    if underline_match:
        text = underline_match.group(1).strip()
        requests.append(get_text_style_request(text, "underline", index))
        chunk = re.sub(r"\_(.+?)\_", text, chunk)

    cleaned_chunk = chunk
    return requests, cleaned_chunk


def parse_markdown_table(markdown_table):
    lines = markdown_table.strip().split("\n")
    table_data = []
    for i, line in enumerate(lines):
        if i == 1:
            continue  # Skip the second row with dashes
        row = [cell.strip() for cell in line.split("|")[1:-1]]
        table_data.append(row)
    return table_data


# Request Generators
def get_header_request(level, text, index):
    # print(f"Applying Header formats: Level {level}, Text: {text}")
    return (
        {"insertText": {"location": {"index": index}, "text": text + "\n"}},
        {
            "updateParagraphStyle": {
                "range": {"startIndex": index, "endIndex": index + len(text) + 1},
                "paragraphStyle": {"namedStyleType": f"HEADING_{level}"},
                "fields": "namedStyleType",
            }
        },
    )


def get_paragraph_request(text, index):
    # print(f"Applying Paragraph formats: Text: {text}")
    return {"insertText": {"location": {"index": index}, "text": text + "\n"}}


def get_text_style_request(text, style, index):
    # print(f"Applying Text Style: Style: {style}, Text: {text}")
    style_mapping = {
        "bold": {"bold": True},
        "italic": {"italic": True},
        "underline": {"underline": True},
    }
    return {
        "updateTextStyle": {
            "range": {"startIndex": index, "endIndex": index + len(text)},
            "textStyle": style_mapping[style],
            "fields": style,
        }
    }


def get_bullet_point_request(text, index):
    # print(f"Applying Bullet formats: Text: {text}")
    return {"insertText": {"location": {"index": index}, "text": text + "\n"}}, {
        "createParagraphBullets": {
            "range": {"startIndex": index, "endIndex": index + len(text) + 1},
            "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
        }
    }


def get_numbered_list_request(text, index):
    # print(f"Applying Numbered List formats: Text: {text}")
    return (
        {"insertText": {"location": {"index": index}, "text": text + "\n"}},
        {
            "createParagraphBullets": {
                "range": {"startIndex": index, "endIndex": index + len(text) + 1},
                "bulletPreset": "NUMBERED_DECIMAL_NESTED",
            }
        },
    )


def get_reset_text_style_request(index):
    return {
        "updateTextStyle": {
            "range": {"startIndex": index, "endIndex": index + 1},
            "textStyle": {},
            "fields": "*",
        }
    }


def get_table_request(table_data, index):
    rows = len(table_data)
    cols = len(table_data[0])
    # print(f"Creating a table of {rows} Rows and {cols} Columns at Index: {index}")
    table_request = {
        "insertTable": {"rows": rows, "columns": cols, "location": {"index": index}}
    }
    return table_request


def get_horizontal_line_request(index):
    return {"insertText": {"location": {"index": index}, "text": "\n"}}, {
        "updateParagraphStyle": {
            "range": {"startIndex": index, "endIndex": index + 1},
            "paragraphStyle": {
                "borderBottom": {
                    "color": {"color": {"rgbColor": {"red": 0, "green": 0, "blue": 0}}},
                    "width": {"magnitude": 1, "unit": "PT"},
                    "padding": {"magnitude": 1, "unit": "PT"},
                    "dashStyle": "SOLID",
                }
            },
            "fields": "borderBottom",
        }
    }


def get_table_content_request(table_data, table_start_index, docs_service, doc_id):
    style_requests = []

    # Accounting for table initiation
    index = table_start_index + 1
    for i_row, row in enumerate(table_data):
        # For each row we increment
        index += 1
        for i_cell, cell in enumerate(row):
            # For each cell we incremenet
            index += 1

            # print("Start Index: ", index)

            received_styles, cleaned_cell = clean_and_capture_styles(cell, index)
            style_requests.extend(received_styles)

            # print(f"Inserting in cell index {index}, content: {cleaned_cell}")
            request = {
                "insertText": {"location": {"index": index}, "text": cleaned_cell}
            }

            docs_service.documents().batchUpdate(
                documentId=doc_id, body={"requests": request}
            ).execute()

            # print("Content: ", cleaned_cell)
            # print("Length of Cell: ", len(cleaned_cell) + 1)

            # Accounting for newline character
            index += len(cleaned_cell) + 1
            # print(f"End Index: {index}\n")

    table_end_index = index + 1

    return style_requests, table_end_index


def insert_image_in_header(doc_id, docs_service, image_url):
    # Step 1: Create the header
    create_header_request = {"createHeader": {"type": "DEFAULT"}}

    # Send request to create the header
    response = (
        docs_service.documents()
        .batchUpdate(documentId=doc_id, body={"requests": [create_header_request]})
        .execute()
    )

    # Retrieve the header ID from the response
    header_id = response.get("replies")[0].get("createHeader").get("headerId")

    # Step 2: Insert the image into the created header aligned to the right
    insert_image_request = {
        "insertInlineImage": {
            "location": {"segmentId": header_id, "index": 0},
            "uri": image_url,
            "objectSize": {
                "height": {"magnitude": 120, "unit": "PT"},
                "width": {"magnitude": 170, "unit": "PT"},
            },
        }
    }

    # Step 3: Align the paragraph containing the image to the right
    align_right_request = {
        "updateParagraphStyle": {
            "range": {"segmentId": header_id, "startIndex": 0, "endIndex": 1},
            "paragraphStyle": {
                "alignment": "END"  # 'END' aligns content to the right
            },
            "fields": "alignment",
        }
    }

    # Step 4: Add space after the image by inserting a newline character
    add_space_request = {
        "insertText": {"location": {"segmentId": header_id, "index": 1}, "text": "\n"}
    }

    # Send all requests to update the header
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [insert_image_request, align_right_request, add_space_request]
        },
    ).execute()


def split_chunks(content):
    lines = content.splitlines()
    clean_lines = []
    skip_next_empty = False

    for i, line in enumerate(lines):
        if line.strip() == "" and skip_next_empty:
            continue

        if re.match(r"^\d+\.\s+(.+)", line.strip()):
            skip_next_empty = True
        else:
            skip_next_empty = False

        clean_lines.append(line)

        # Peek at the next line
        if i < len(lines) - 1:
            next_line = lines[i + 1].strip()
            if (
                line.strip() != ""
                and next_line == ""
                and re.match(r"^\d+\.\s+(.+)", lines[i + 2].strip())
            ):
                continue
            if re.match(r"^\d+\.\s+(.+)", line.strip()) and next_line == "":
                clean_lines.append("")

    return "\n".join(clean_lines)


def rate_limited_batch_update(docs_service, doc_id, requests, rate_limit=120):
    batch_size = rate_limit
    for i in range(0, len(requests), batch_size):
        batch_requests = requests[i : i + batch_size]
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": batch_requests}
        ).execute()


# Update Google Doc Content with Rate Limiting
def update_google_doc_content(doc_id, docs_service, content_markdown):
    content_markdown = split_chunks(content_markdown)
    chunks = re.split(r"(?<=\n)", content_markdown)
    chunks = iter(chunks)
    index = 1
    all_requests = []

    for chunk in chunks:
        chunk = chunk.strip()
        requests = []
        style_requests = []

        # Clean the chunk and capture style requests
        received_styling, cleaned_chunk = clean_and_capture_styles(chunk, index)
        style_requests.extend(received_styling)

        header_match = re.match(r"^(#{1,6})\s+(.+)", cleaned_chunk)
        bullet_point_match = re.match(r"^-\s+(.+)", cleaned_chunk)
        numbered_list_match = re.match(r"^\d+\.\s+(.+)", cleaned_chunk)
        table_match = re.match(r"^\|.+\|", cleaned_chunk)

        if header_match:
            header_level = len(re.match(r"^#+", cleaned_chunk).group(0))
            text = cleaned_chunk[header_level:].strip()
            requests.extend(get_header_request(header_level, text, index))
        elif bullet_point_match:
            text = cleaned_chunk[2:].strip()
            requests.extend(get_bullet_point_request(text, index))
        elif numbered_list_match:
            text = re.sub(r"^\d+\.\s", "", cleaned_chunk).strip()
            requests.extend(get_numbered_list_request(text, index))
        elif cleaned_chunk == "---":
            requests.extend(get_horizontal_line_request(index))
        elif table_match:
            # If it's a table, first process everything already there in all_requests, then clear it
            rate_limited_batch_update(docs_service, doc_id, all_requests)
            all_requests.clear()

            table_lines = [chunk]
            while True:
                try:
                    next_chunk = next(chunks).strip()
                    if re.match(r"^\|.+\|", next_chunk):
                        table_lines.append(next_chunk)
                    else:
                        break
                except StopIteration:
                    break

            table_data = parse_markdown_table("\n".join(table_lines))
            table_request = get_table_request(table_data, index)

            docs_service.documents().batchUpdate(
                documentId=doc_id, body={"requests": table_request}
            ).execute()

            content = (
                docs_service.documents()
                .get(documentId=doc_id, fields="body")
                .execute()
                .get("body")
                .get("content")
            )
            tables = [c for c in content if c.get("table")]
            table_start_index = tables[-1]["startIndex"]
            received_styles, table_end_index = get_table_content_request(
                table_data, table_start_index, docs_service, doc_id
            )
            style_requests.extend(received_styles)
            index = table_end_index
            requests.append(get_paragraph_request("\n", index))
        else:
            requests.append(get_paragraph_request(cleaned_chunk, index))

        for req_tuple in requests:
            if isinstance(req_tuple, tuple):
                for req in req_tuple:
                    all_requests.append(req)
                    if "insertText" in req:
                        index += len(req["insertText"]["text"])
            else:
                all_requests.append(req_tuple)
                if "insertText" in req_tuple:
                    index += len(req_tuple["insertText"]["text"])

        for req in style_requests:
            all_requests.append(req)

        all_requests.append(get_reset_text_style_request(index))

    rate_limited_batch_update(docs_service, doc_id, all_requests)


def generate_google_docs(content_in_bytes):
    document_title = "PlanBright AI Google Doc"
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # header_image_path = os.path.join(current_dir, "../unconstrained_logo.png")

    start = time.time()
    doc_id, doc_url = create_empty_google_doc(document_title)

    # Build the google docs service route
    _, docs_service = authenticate_google_services()

    end = time.time()

    # Thread to insert the image in the header
    def insert_image():
        # Build the google docs service route
        _, docs_service_image = authenticate_google_services()
        insert_image_in_header(doc_id, docs_service_image, BRANDING_IMAGE_URL)

    # Thread to upload the content
    def upload_content():
        _, docs_service_content = authenticate_google_services()
        content_markdown = content_in_bytes.getvalue().decode("utf-8")
        update_google_doc_content(doc_id, docs_service_content, content_markdown)

    # Start the threads asynchronously
    image_thread = threading.Thread(target=insert_image)
    content_thread = threading.Thread(target=upload_content)

    image_thread.start()
    content_thread.start()

    print(f"Elapsed Time = {end-start} seconds")
    return doc_url


# ========================================================================================================================


def clean_and_join_text(text):
    symbols_to_remove = ["-----"]
    lines = text.split("\n")
    lines = [
        line
        for line in lines
        if not any(symbol in line for symbol in symbols_to_remove)
    ]
    cleaned_lines = []
    current_paragraph = []
    heading_pattern = re.compile(r"^\s*#+\s+")
    list_pattern = re.compile(r"^\s*[-*◦]\s+")
    number_list_pattern = re.compile(r"^\s*\d+\.\s+")
    table_row_pattern = re.compile(r"^\s*\|\s*.*\|\s*.*\|\s*.*\|\s*$")

    for line in lines:
        if heading_pattern.match(line):
            if current_paragraph:
                cleaned_lines.append(" ".join(current_paragraph))
                current_paragraph = []
            cleaned_lines.append(line)
        elif list_pattern.match(line) or number_list_pattern.match(line):
            if current_paragraph:
                cleaned_lines.append(" ".join(current_paragraph))
                current_paragraph = []
            cleaned_lines.append(line.strip())
        elif table_row_pattern.match(line):
            if current_paragraph:
                cleaned_lines.append(" ".join(current_paragraph))
                current_paragraph = []
            cleaned_lines.append(line)
        else:
            if line.strip():
                current_paragraph.append(line.strip())

    if current_paragraph:
        cleaned_lines.append(" ".join(current_paragraph))

    return "\n".join(cleaned_lines)


# Helper function which allows to summarize (bullet points or paragraph), make it simpler, shorter, longer or make more professional
# Depending on the transformaation_func call - abstracted for all microapps, several key inputs are needed to map to the right microapp chat
async def process_and_save_response(
    response_id: str,
    transformation_func: callable,
    unique_id_creator: callable,
    complete_response: callable,
    agent_details: dict,
    storage: SupabaseStorage,
):
    # init_args = agent_details.get("init_args", {})
    # agent_class = agent_details["class"](**init_args)
    # response_field = agent_details["response_field"]
    storage_method = getattr(storage, agent_details["storage_method_for_quick_action"])
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

    # Retrieve the original chat message from the database using the response_id
    chat_message = storage.fetch_by_id(
        first_table_name,
        second_table_name,
        third_tabel_name,
        response_id,
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

    # Check if 'quick_action' is in the table name
    if "quick_action" in chat_message[0].table_name:
        response_id = chat_message[1]
        chat_message[0].table_name = chat_message[2]

    # Apply the transformation function to the original response
    return EventSourceResponse(
        content=transformation_func(
            chat_message[0].response,
            chat_message[0].table_name,
            response_id,
            storage_method,
            unique_id_creator,
            complete_response,
        )
    )

    # Update the existing entry with the summarized response
    # update_data = {"summarized_response": transformed_text}
    # update_success = storage.update_entry(
    # table_name, id_column, response_id, update_data
    # )

    # if not update_success:
    # raise HTTPException(
    # status_code=500, detail="Failed to update summarized response"
    # )


async def process_and_save_response_for_aicoach(
    response_id: str,
    transformation_func: callable,
    unique_id_creator: callable,
    complete_response: callable,
    agent_details: dict,
    storage: SupabaseStorage,
):
    # init_args = agent_details.get("init_args", {})
    # agent_class = agent_details["class"](**init_args)
    # response_field = agent_details["response_field"]
    storage_method = getattr(storage, agent_details["storage_method_for_quick_action"])
    model = agent_details["model"]
    first_table_name = agent_details["table_name_one"]
    second_table_name = agent_details["table_name_two"]
    id_column_one = agent_details["id_column_one"]
    id_column_two = agent_details["id_column_two"]
    response_field_one = agent_details["response_field_one"]
    response_field_two = agent_details["response_field_two"]
    session_id = agent_details["session_id"]
    refrence_id = agent_details["refrence_id"]
    # response_field = agent_details["response_field"]

    # Retrieve the original chat message from the database using the response_id
    chat_message, required_id = storage.fetch_by_id_for_aicoach(
        first_table_name=first_table_name,
        second_table_name=second_table_name,
        record_id=response_id,
        id_column_one=id_column_one,
        id_column_two=id_column_two,
        response_field_one=response_field_one,
        response_field_two=response_field_two,
        session_id=session_id,
        refrence_id=refrence_id,
        model=model,
    )
    if not chat_message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    # Check if 'quick_action' is in the table name
    if "quick_action" in chat_message.table_name:
        response_id = required_id

    # Apply the transformation function to the original response
    return EventSourceResponse(
        content=transformation_func(
            chat_message.response,
            chat_message.table_name,
            response_id,
            storage_method,
            unique_id_creator,
            complete_response,
        )
    )
    # Update the existing entry with the summarized response
    # update_data = {"summarized_response": transformed_text}
    # update_success = storage.update_entry(
    # table_name, id_column, response_id, update_data
    # )

    # if not update_success:
    # raise HTTPException(
    # status_code=500, detail="Failed to update summarized response"
    # )
