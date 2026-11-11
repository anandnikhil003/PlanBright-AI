from personalization.database.manager import SupabaseConnectionManager
from personalization.database.schemas.historical_asset import HistoricalAssetCreate
from fastapi import HTTPException


class HistoricalAssetCRUD:
    def __init__(self, schema: str):
        self.db = SupabaseConnectionManager(schema=schema).get_client()

    def create_asset(self, asset_data: HistoricalAssetCreate):
        try:
            result = (
                self.db.table("historical_assets").insert(asset_data.dict()).execute()
            )
            # Assuming result.data contains a list, extract the first item
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to create asset: No data returned"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create asset: {e}")

    def get_asset(self, asset_id: int):
        try:
            result = (
                self.db.table("historical_assets")
                .select("*")
                .eq("id", asset_id)
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status_code=404, detail="Asset not found")
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve asset: {e}"
            )

    def update_asset(self, asset_id: int, asset_data: HistoricalAssetCreate):
        try:
            result = (
                self.db.table("historical_assets")
                .update(asset_data.dict())
                .eq("id", asset_id)
                .execute()
            )
            # Assuming result.data contains a list, extract the first item
            if result.data:
                return result.data[0]  # Return the first item in the list
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to update  asset: No data returned"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update asset: {e}")

    def delete_asset(self, asset_id: int):
        try:
            self.db.table("historical_assets").delete().eq("id", asset_id).execute()
            return {"message": "Asset deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete asset: {e}")
