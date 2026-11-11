import os
from typing import Optional
class LocalStorage:

    def __init__(self) -> None:
        self.root_dir = "./generated_data"
    
    def save_lesson_plan(self, id, lesson_plan):
        with open(f"{self.root_dir}/{id}.md", "w") as f:
            f.write(lesson_plan)
    
    def get_lesson_plan_by_id(self, id: str) -> Optional[str]:
        if not os.path.exists(f"{self.root_dir}/{id}.md"):
            return None
        return f"{self.root_dir}/{id}.md"

def get_local_storage() -> LocalStorage:
    if not hasattr(get_local_storage, "instance"):
        get_local_storage.instance = LocalStorage()
    return get_local_storage.instance