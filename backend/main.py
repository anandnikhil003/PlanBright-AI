import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routes.lesson_planner_route import lesson_planner_router
from routes.assesment_generator_route import assesment_generator_router
from routes.rubrik_generator_route import rubrik_generator_router
from routes.diffrentiation_suggestor_route import diffrentiation_suggestor_router
from routes.ai_coach_route import coach_router
from routes.apps_interaction_route import apps_interaction_router
from routes.iep_generator_route import iep_generator_router
from security.auth import verify_token
from routes.db_health_check_route import db_health_check_router
from routes.uploadˍfiles_route import upload_file_router
from routes.unit_planner_route import unit_planner_router
from routes.feedback_generator_route import feedback_generator_router
from routes.share_link_route import share_link_router
from personalization.apis.routes import personalization_router
from bot.apis.entity.bot_entity import bots
from bot.apis.entity.bot_file_entity import bots_files
from bot.apis.entity.embedding_entity import bots_embeddings
from bot.apis.entity.bot_engagement_entity import bots_engagement
import re


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting PlanBright AI backend")
    app.include_router(lesson_planner_router)
    app.include_router(assesment_generator_router)
    app.include_router(rubrik_generator_router)
    app.include_router(diffrentiation_suggestor_router)
    app.include_router(coach_router)
    app.include_router(apps_interaction_router)
    app.include_router(db_health_check_router)
    app.include_router(iep_generator_router)
    app.include_router(upload_file_router)
    app.include_router(unit_planner_router)
    app.include_router(feedback_generator_router)
    app.include_router(share_link_router)
    app.include_router(personalization_router)
    app.include_router(bots)
    app.include_router(bots_files)
    app.include_router(bots_embeddings)
    app.include_router(bots_engagement)
    yield
    print("stopping PlanBright AI backend")


app = FastAPI(
    lifespan=lifespan,
    title="PlanBright AI",
    description="Backend APIs for PlanBright AI teaching tools",
    version="0.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# List of full paths to exclude from authentication
EXCLUDE_PATHS = [
    "/api/db_health_check/health_check",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
    "/api/bots_creations/iframe_bot_history",
    r"^/api/bots_creations/bots/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",  # Dynamic path for UUIDs
]


# Middleware to validate token
@app.middleware("http")
async def check_authentication(request, call_next):
    path = request.url.path

    # Check if the path matches any static paths
    if path in [p for p in EXCLUDE_PATHS if not p.startswith("^")]:
        return await call_next(request)

    # Check if the path matches any regex dynamic paths
    for pattern in [p for p in EXCLUDE_PATHS if p.startswith("^")]:
        if re.match(pattern, path):
            return await call_next(request)

    # Token validation for other paths
    token = request.headers.get("token")
    user_id = verify_token(token)
    if not user_id:
        return JSONResponse({"detail": "Invalid token"}, status_code=401)
    request.state.user_id = str(user_id)
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
