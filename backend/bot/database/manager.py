from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from dotenv import load_dotenv
import os

load_dotenv()


## creating databse client
class DatabaseManager:
    def __init__(self, schema="public"):
        self.schema = schema
        self.db: Client = create_client(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY"),
            options=ClientOptions(schema=schema),
        )

    def get_client(self) -> Client:
        return self.db
