from fastapi import APIRouter, Depends
from personalization.database.schemas.school import SchoolCreate, School
from personalization.database.schemas.teacher import TeacherCreate, Teacher
from personalization.database.schemas.historical_asset import (
    HistoricalAssetCreate,
    HistoricalAsset,
)
from personalization.database.schemas.course_material import (
    CourseMaterialCreate,
    CourseMaterial,
)
from personalization.database.schemas.embedding import EmbeddingCreate, Embedding
from personalization.database.schemas.ai_generated import (
    AIGeneratedOutputCreate,
    AIGeneratedOutput,
)

from personalization.apis.entities.school_function import SchoolCRUD
from personalization.apis.entities.teacher_function import TeacherCRUD
from personalization.apis.entities.historical_asset_function import HistoricalAssetCRUD
from personalization.apis.entities.course_material_function import CourseMaterialCRUD
from personalization.apis.entities.embedding_functions import EmbeddingCRUD
from personalization.apis.entities.ai_generated_functions import AIGeneratedOutputCRUD


personalization_router = APIRouter(
    prefix="/api/personalization", tags=["personalization"]
)


# Dependency to retrieve SchoolCRUD and TeacherCRUD instances with the appropriate schema
def get_school_crud(schema: str = "school_dhaka"):
    return SchoolCRUD(schema)


def get_teacher_crud(schema: str = "school_dhaka"):
    return TeacherCRUD(schema)


def get_historical_asset_crud(schema: str = "school_dhaka"):
    return HistoricalAssetCRUD(schema)


def get_course_material_crud(schema: str = "school_dhaka"):
    return CourseMaterialCRUD(schema)


def get_embedding_crud(schema: str = "school_dhaka"):
    return EmbeddingCRUD(schema)


def get_ai_generated_output_crud(schema: str = "school_dhaka"):
    return AIGeneratedOutputCRUD(schema)


# School endpoints
@personalization_router.post("/schools", response_model=School)
async def create_school_endpoint(
    school: SchoolCreate, school_crud: SchoolCRUD = Depends(get_school_crud)
):
    return await school_crud.create_school(school)


@personalization_router.get("/schools/{school_id}", response_model=School)
async def read_school(
    school_id: str, school_crud: SchoolCRUD = Depends(get_school_crud)
):
    return school_crud.get_school(school_id)


@personalization_router.put("/schools/{school_id}", response_model=School)
async def update_school_endpoint(
    school_id: str,
    school: SchoolCreate,
    school_crud: SchoolCRUD = Depends(get_school_crud),
):
    return school_crud.update_school(school_id, school)


@personalization_router.delete("/schools/{school_id}")
async def delete_school_endpoint(
    school_id: str, school_crud: SchoolCRUD = Depends(get_school_crud)
):
    return school_crud.delete_school(school_id)


# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------


# Teacher endpoints
@personalization_router.post("/teachers", response_model=Teacher)
async def create_teacher_endpoint(
    teacher: TeacherCreate, teacher_crud: TeacherCRUD = Depends(get_teacher_crud)
):
    return teacher_crud.create_teacher(teacher)


@personalization_router.get("/teachers/{teacher_id}", response_model=Teacher)
async def read_teacher(
    teacher_id: str, teacher_crud: TeacherCRUD = Depends(get_teacher_crud)
):
    return teacher_crud.get_teacher(teacher_id)


@personalization_router.put("/teachers/{teacher_id}", response_model=Teacher)
async def update_teacher_endpoint(
    teacher_id: str,
    teacher: TeacherCreate,
    teacher_crud: TeacherCRUD = Depends(get_teacher_crud),
):
    return teacher_crud.update_teacher(teacher_id, teacher)


@personalization_router.delete("/teachers/{teacher_id}")
async def delete_teacher_endpoint(
    teacher_id: str, teacher_crud: TeacherCRUD = Depends(get_teacher_crud)
):
    return teacher_crud.delete_teacher(teacher_id)


# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------


# Historical Asset Endpoints
@personalization_router.post("/historical_assets", response_model=HistoricalAsset)
async def create_historical_asset(
    asset: HistoricalAssetCreate,
    asset_crud: HistoricalAssetCRUD = Depends(get_historical_asset_crud),
):
    return asset_crud.create_asset(asset)


@personalization_router.get(
    "/historical_assets/{asset_id}", response_model=HistoricalAsset
)
async def read_historical_asset(
    asset_id: str, asset_crud: HistoricalAssetCRUD = Depends(get_historical_asset_crud)
):
    return asset_crud.get_asset(asset_id)


@personalization_router.put(
    "/historical_assets/{asset_id}", response_model=HistoricalAsset
)
async def update_historical_asset(
    asset_id: str,
    asset: HistoricalAssetCreate,
    asset_crud: HistoricalAssetCRUD = Depends(get_historical_asset_crud),
):
    return asset_crud.update_asset(asset_id, asset)


@personalization_router.delete("/historical_assets/{asset_id}")
async def delete_historical_asset(
    asset_id: str, asset_crud: HistoricalAssetCRUD = Depends(get_historical_asset_crud)
):
    return asset_crud.delete_asset(asset_id)


# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------


# Course Material Endpoints
@personalization_router.post("/course_materials", response_model=CourseMaterial)
async def create_course_material(
    material: CourseMaterialCreate,
    material_crud: CourseMaterialCRUD = Depends(get_course_material_crud),
):
    return material_crud.create_course_material(material)


@personalization_router.get(
    "/course_materials/{material_id}", response_model=CourseMaterial
)
async def read_course_material(
    material_id: str,
    material_crud: CourseMaterialCRUD = Depends(get_course_material_crud),
):
    return material_crud.get_course_material(material_id)


@personalization_router.put(
    "/course_materials/{material_id}", response_model=CourseMaterial
)
async def update_course_material(
    material_id: str,
    material: CourseMaterialCreate,
    material_crud: CourseMaterialCRUD = Depends(get_course_material_crud),
):
    return material_crud.update_course_material(material_id, material)


@personalization_router.delete("/course_materials/{material_id}")
async def delete_course_material(
    material_id: str,
    material_crud: CourseMaterialCRUD = Depends(get_course_material_crud),
):
    return material_crud.delete_course_material(material_id)


# creating custom api for course material
@personalization_router.get("/course_materials/{school_id}")
async def get_course_material_for_schoolid(
    school_id: str,
    material_crud: CourseMaterialCRUD = Depends(get_course_material_crud),
):
    return material_crud.get_course_for_school(school_id=school_id)


# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------


# Embedding Endpoints
@personalization_router.post("/embeddings", response_model=Embedding)
async def create_embedding(
    embedding: EmbeddingCreate,
    embedding_crud: EmbeddingCRUD = Depends(get_embedding_crud),
):
    return embedding_crud.create_embedding(embedding)


@personalization_router.get("/embeddings/{embedding_id}", response_model=Embedding)
async def read_embedding(
    embedding_id: str, embedding_crud: EmbeddingCRUD = Depends(get_embedding_crud)
):
    return embedding_crud.get_embedding(embedding_id)


@personalization_router.put("/embeddings/{embedding_id}", response_model=Embedding)
async def update_embedding(
    embedding_id: str,
    embedding: EmbeddingCreate,
    embedding_crud: EmbeddingCRUD = Depends(get_embedding_crud),
):
    return embedding_crud.update_embedding(embedding_id, embedding)


@personalization_router.delete("/embeddings/{embedding_id}")
async def delete_embedding(
    embedding_id: str, embedding_crud: EmbeddingCRUD = Depends(get_embedding_crud)
):
    return embedding_crud.delete_embedding(embedding_id)


# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------


# AI Generated Output Endpoints
@personalization_router.post("/ai_generated_outputs", response_model=AIGeneratedOutput)
async def create_ai_generated_output(
    output: AIGeneratedOutputCreate,
    output_crud: AIGeneratedOutputCRUD = Depends(get_ai_generated_output_crud),
):
    return output_crud.create_output(output)


@personalization_router.get(
    "/ai_generated_outputs/{output_id}", response_model=AIGeneratedOutput
)
async def read_ai_generated_output(
    output_id: str,
    output_crud: AIGeneratedOutputCRUD = Depends(get_ai_generated_output_crud),
):
    return output_crud.get_output(output_id)


@personalization_router.put(
    "/ai_generated_outputs/{output_id}", response_model=AIGeneratedOutput
)
async def update_ai_generated_output(
    output_id: str,
    output: AIGeneratedOutputCreate,
    output_crud: AIGeneratedOutputCRUD = Depends(get_ai_generated_output_crud),
):
    return output_crud.update_output(output_id, output)


@personalization_router.delete("/ai_generated_outputs/{output_id}")
async def delete_ai_generated_output(
    output_id: str,
    output_crud: AIGeneratedOutputCRUD = Depends(get_ai_generated_output_crud),
):
    return output_crud.delete_output(output_id)
