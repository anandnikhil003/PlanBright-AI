from fastapi import APIRouter, Depends
from bot.database.schemas.bot_engagement import BotEngagementCreate, BotEngagement
from bot.database.crud.bot_engagement import BotEngagementCRUD

bots_engagement = APIRouter(prefix="/api/bots_engagement", tags=["Bots_Engagement"])


def get_bot_engagement_crud():
    return BotEngagementCRUD()


@bots_engagement.post("/bots/{bot_id}/engagement", response_model=BotEngagement)
async def create_bot_engagement(
    bot_id: str,
    engagement: BotEngagementCreate,
    bot_engagement_crud: BotEngagementCRUD = Depends(get_bot_engagement_crud),
):
    engagement.bot_id = bot_id  # Set the bot_id from the URL parameter
    return bot_engagement_crud.create_bot_engagement(engagement)


@bots_engagement.get("/bots/{bot_id}/engagement", response_model=list[BotEngagement])
async def list_bot_engagements(
    bot_id: str,
    bot_engagement_crud: BotEngagementCRUD = Depends(get_bot_engagement_crud),
):
    return bot_engagement_crud.get_bot_engagements(bot_id)


@bots_engagement.get("/bots/engagement/{engagement_id}", response_model=BotEngagement)
async def read_bot_engagement(
    engagement_id: str,
    bot_engagement_crud: BotEngagementCRUD = Depends(get_bot_engagement_crud),
):
    return bot_engagement_crud.get_bot_engagement(engagement_id)


@bots_engagement.put("/bots/engagement/{engagement_id}", response_model=BotEngagement)
async def update_bot_engagement(
    engagement_id: str,
    engagement: BotEngagementCreate,
    bot_engagement_crud: BotEngagementCRUD = Depends(get_bot_engagement_crud),
):
    return bot_engagement_crud.update_bot_engagement(engagement_id, engagement)


@bots_engagement.delete("/bots/engagement/{engagement_id}")
async def delete_bot_engagement(
    engagement_id: str,
    bot_engagement_crud: BotEngagementCRUD = Depends(get_bot_engagement_crud),
):
    return bot_engagement_crud.delete_bot_engagement(engagement_id)
