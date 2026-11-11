from fastapi import APIRouter, HTTPException, Request, Depends
from db.remote_storage import SupabaseStorage, get_storage
from models.data_models import ShareSessionID
import time
import json
from config.agent_details import AGENT_DETAILS

share_link_router = APIRouter(prefix="/api/share_link", tags=["Share Link"])


@share_link_router.put("/share_url/{source}/{id}")
async def get_share_link_url(
    request: Request,
    source: str,
    id: str,
    storage: SupabaseStorage = Depends(get_storage),
) -> ShareSessionID:
    start_time = time.time()
    print(
        f"API endpoint hit at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
    )

    user_id = request.state.user_id

    try:
        if source == "ai_coach":
            session_id = storage.fetch_session_id(id)
            id = session_id
            if session_id:
                storage.add_share_link_url(user_id, source, id)
                return ShareSessionID(id=id)
            else:
                raise HTTPException(
                    status_code=404,
                    detail="An error occurred while fetching session id or session id not found",
                )
        storage.add_share_link_url(user_id, source, id)
        end_time = time.time()
        print(
            f"API response completed at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
        )
        print(f"Total time taken: {end_time - start_time:.2f} seconds")
        return ShareSessionID(id=id)
    except Exception as e:
        end_time = time.time()
        print(
            f"API response encountered an error at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
        )
        print(f"Total time taken until error: {end_time - start_time:.2f} seconds")
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred while storing the share link URL"
        )


@share_link_router.get("/url_data/{source}/{id}")
async def data_for_share_url(
    source: str,
    id: str,
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        start_time = time.time()
        url_data = storage.return_data_for_url(id, source)
        url_updated_data = storage.get_chat_history_list(id)
        print(url_data)
        print(type(url_data))
        if not url_data or url_data != url_updated_data:
            print(source, id)
            if source == "ai_coach":
                url_data = storage.get_chat_history_list(id)
            else:
                agent_details = AGENT_DETAILS[source]
                url_data = storage.get_agent_plan(id, agent_details)

            # Convert list of Pydantic instances to list of dictionaries
            url_data_dicts = [item.dict() for item in url_data]
            # Serialize list of dictionaries to JSON string
            url_data_json = json.dumps(url_data_dicts, default=str)
            udpdated_response_data = storage.update_response_data_of_share_link(
                id, source, url_data_json
            )
            print(udpdated_response_data)
            end_time = time.time()
            print(
                f"API response completed at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
            )
            print(f"Total time taken: {end_time - start_time:.2f} seconds")
            return url_data
        end_time = time.time()
        print(
            f"API response completed at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
        )
        print(f"Total time taken: {end_time - start_time:.2f} seconds")
        return url_data
    except Exception as e:
        end_time = time.time()
        print(
            f"API response encountered an error at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
        )
        print(f"Total time taken until error: {end_time - start_time:.2f} seconds")
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred while storing the share link URL"
        )
