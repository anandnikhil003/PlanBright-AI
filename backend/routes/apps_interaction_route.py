from fastapi import APIRouter, Depends, Request
from models.data_models import TotalInteractionResponse
from db.interaction_manager import InteractionManager, get_interaction_manager
from db.remote_storage import SupabaseStorage, get_storage
from models.data_models import NewTags
import time

# final changes to check automatic deployment


apps_interaction_router = APIRouter(
    prefix="/api/apps_interaction", tags=["Total Interaction Count"]
)


@apps_interaction_router.get(path="/total_interactions")
async def get_total_interactions(
    request: Request,
    interaction_manager: InteractionManager = Depends(get_interaction_manager),
) -> TotalInteractionResponse:
    user_id = request.state.user_id
    count = interaction_manager.calculate_total_interactions(user_id)
    return TotalInteractionResponse(user_id=user_id, overall_interaction=count)


@apps_interaction_router.get(path="/new_tags_names")
async def get_toal_new_tags(
    request: Request,
    storage: SupabaseStorage = Depends(get_storage),
) -> NewTags:
    start_time = time.time()
    user_id = request.state.user_id

    newTagArr = ["iep", "feedbackgenerator", "unitplanner"]

    response = (
        storage.db.table("uc_apps_interaction")
        .select("IEP_count, feedback_count, unit_count")
        .eq("user_id", user_id)
        .execute()
    )
    response_data = response.data

    if not response_data:
        print(f"Execution time: {time.time() - start_time:.4f} seconds")
        return NewTags(new_tag=newTagArr)

    # Mapping field names to their corresponding new tag values
    tag_mapping = {
        "IEP_count": "iep",
        "feedback_count": "feedbackgenerator",
        "unit_count": "unitplanner",
    }

    # Iterate over the tag_mapping and adjust newTagArr based on the count value
    finalTags = []
    for count_key, tag in tag_mapping.items():
        if response_data[0].get(count_key) is None:
            finalTags.append(tag)

    print(f"Execution time: {time.time() - start_time:.4f} seconds")
    return NewTags(new_tag=finalTags)


@apps_interaction_router.get(path="/used_microapps_list")
async def get_toal_microapps_used(
    request: Request,
    storage: SupabaseStorage = Depends(get_storage),
) -> NewTags:
    start_time = time.time()
    user_id = request.state.user_id

    # newTagArr = ['lessonplanner', 'rubrikgenerator', 'assessmentgenerator', 'diffrentiationgenerator', 'iep', 'feedbackgenerator', 'unitplanner']

    response = (
        storage.db.table("uc_apps_interaction")
        .select(
            "lesson_planner_count, rubrik_count, assessment_count, diffrentiation_count, IEP_count, feedback_count, unit_count"
        )
        .eq("user_id", user_id)
        .execute()
    )
    response_data = response.data

    if not response_data:
        print(f"Execution time: {time.time() - start_time:.4f} seconds")
        return NewTags(new_tag=[])

    # Mapping field names to their corresponding new tag values
    tag_mapping = {
        "lesson_planner_count": "lesson_planner",
        "rubrik_count": "rubrik_generator",
        "assessment_count": "assesment_generator",
        "diffrentiation_count": "diffrentiation_suggestor",
        "IEP_count": "iep_generator",
        "feedback_count": "feedback_generator",
        "unit_count": "unit_planner",
    }

    # Iterate over the tag_mapping and adjust newTagArr based on the count value
    finalTags = []
    for count_key, tag in tag_mapping.items():
        if response_data[0].get(count_key) is not None:
            finalTags.append(tag)

    print(f"Execution time: {time.time() - start_time:.4f} seconds")
    return NewTags(new_tag=finalTags)
