from fastapi import APIRouter, HTTPException, Request, Depends
from db.interaction_manager import InteractionManager, get_interaction_manager


db_health_check_router = APIRouter(
    prefix="/api/db_health_check", tags=["Database connection check"]
)


@db_health_check_router.get(path="/health_check")
async def check_connection(
    request: Request,
    interaction_manager: InteractionManager = Depends(get_interaction_manager),
):
    if await interaction_manager.check_db_connection():
        return {"status": "success", "message": "Database connection successful"}
    else:
        raise HTTPException(status_code=500, detail="Database connection failed")
