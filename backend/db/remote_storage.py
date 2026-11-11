import os
import json
import io
from dateutil import parser
from typing import Optional, List, Type, Union
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from models.data_models import (
    CleanedHistoryResponse,
    IDList,
    ChatHistoryListItem,
    GenerateLessonPlan,
    GenerateAssessmentEdit,
    GenerateDiffrentiation,
    GenerateRubrik,
    GenerateUnitPlan,
    FavoriteRequest,
    GenerateIEP,
    GenerateFeedback,
    AgentMainItem,
    GenerateAssessment,
)
from datetime import timedelta
from dateutil import parser
# from config.agent_details import AGENT_DETAILS

load_dotenv()


class SupabaseStorage:
    def __init__(self):
        self.db: Client = create_client(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY"),
        )

    def add_lesson_plan(
        self, lesson_plan_id, user_query, lesson_plan, user_id, summary_title
    ):
        values = {
            "lesson_plan_id": lesson_plan_id,
            "user_query": user_query,
            "lesson_plan": lesson_plan,
            "user_id": user_id,
            "summary_title": summary_title,
        }
        try:
            self.db.table("uc_lesson_planner").insert(values).execute()
            print("lesson plan added")
        except Exception as e:
            print(e)

    def add_interactive_chat(self, chat_msg_id, user_query, coach_response, history_id):
        values = {
            "chat_msg_id": chat_msg_id,
            "user_query": user_query,
            "coach_response": coach_response,
            "history_id": history_id,
        }
        try:
            self.db.table("uc_chat_msg").insert(values).execute()
            print("chat messages added")
        except Exception as e:
            print(e)

    def add_diffrentiation_chat(
        self, chat_msg_id, user_query, chat_response, diffrentiation_history_id
    ):
        values = {
            "chat_msg_id": chat_msg_id,
            "user_query": user_query,
            "chat_response": chat_response,
            "diffrentiation_history_id": diffrentiation_history_id,
        }
        try:
            self.db.table("uc_diffrentiation_chat").insert(values).execute()
            print("chat messages added")
        except Exception as e:
            print(e)

    def add_unitplan_chat(
        self, chat_msg_id, user_query, chat_response, unitplan_history_id
    ):
        values = {
            "chat_msg_id": chat_msg_id,
            "user_query": user_query,
            "chat_response": chat_response,
            "unitplan_history_id": unitplan_history_id,
        }
        try:
            self.db.table("uc_unitplan_chat").insert(values).execute()
            print("chat messages added")
        except Exception as e:
            print(e)

    def add_share_link_url(self, user_id, source, response_id):
        values = {
            "user_id": user_id,
            "source": source,
            "response_id": response_id,
        }
        try:
            self.db.table("uc_share_url_data").insert(values).execute()
            print("chat messages added")
        except Exception as e:
            print(e)

    def add_iep_chat(self, chat_msg_id, user_query, chat_response, iep_history_id):
        values = {
            "chat_msg_id": chat_msg_id,
            "user_query": user_query,
            "chat_response": chat_response,
            "iep_history_id": iep_history_id,
        }
        try:
            self.db.table("uc_IEP_chat").insert(values).execute()
            print("chat messages added")
        except Exception as e:
            print(e)

    def add_feedback_chat(
        self, chat_msg_id, user_query, chat_response, feedback_generator_history_id
    ):
        values = {
            "chat_msg_id": chat_msg_id,
            "user_query": user_query,
            "chat_response": chat_response,
            "feedback_generator_history_id": feedback_generator_history_id,
        }
        try:
            self.db.table("uc_feedback_generator_chat").insert(values).execute()
            print("chat messages added")
        except Exception as e:
            print(e)

    def add_assessment_chat(
        self, chat_msg_id, user_query, chat_response, assessment_history_id
    ):
        values = {
            "chat_msg_id": chat_msg_id,
            "user_query": user_query,
            "chat_response": chat_response,
            "assessment_history_id": assessment_history_id,
        }
        try:
            self.db.table("uc_assesment_chat").insert(values).execute()
            print("chat messages added")
        except Exception as e:
            print(e)

    def add_lesson_plan_chat(
        self, chat_msg_id, user_query, chat_response, lesson_history_id
    ):
        values = {
            "chat_msg_id": chat_msg_id,
            "user_query": user_query,
            "chat_response": chat_response,
            "lesson_history_id": lesson_history_id,
        }
        try:
            self.db.table("uc_lesson_planner_chat").insert(values).execute()
            print("chat messages added")
        except Exception as e:
            print(e)

    def add_rubrik_chat(
        self, chat_msg_id, user_query, chat_response, rubrik_history_id
    ):
        values = {
            "chat_msg_id": chat_msg_id,
            "user_query": user_query,
            "chat_response": chat_response,
            "rubrik_history_id": rubrik_history_id,
        }
        try:
            self.db.table("uc_rubrik_chat").insert(values).execute()
            print("chat messages added")
        except Exception as e:
            print(e)

    def add_rubrik(
        self, rubrik_id, user_query, rubrik_response, user_id, summary_title
    ):
        values = {
            "rubrik_id": rubrik_id,
            "user_query": user_query,
            "rubrik_response": rubrik_response,
            "user_id": user_id,
            "summary_title": summary_title,
        }
        try:
            self.db.table("uc_rubrik_generator").insert(values).execute()
            print("rubrik response added")
        except Exception as e:
            print(e)

    def add_assesment(
        self, assesment_id, user_query, assesment_response, user_id, summary_title
    ):
        values = {
            "assessment_id": assesment_id,
            "user_query": user_query,
            "assesment_response": assesment_response,
            "user_id": user_id,
            "summary_title": summary_title,
        }
        try:
            self.db.table("uc_assesment_generator").insert(values).execute()
            print("assesment response added")
        except Exception as e:
            print(e)

    def add_chat_quick_action(
        self,
        action_id,
        action_query,
        action_response,
        original_id,
        action_type,
        table_name,
    ):
        values = {
            "action_id": action_id,
            "action_query": action_query,
            "action_response": action_response,
            "chat_msg_id": original_id,
            "action_type": action_type,
        }
        try:
            self.db.table("uc_chat_quick_action").insert(values).execute()
            print("chat response added")
        except Exception as e:
            print(e)

    def add_lessonplan_quick_action(
        self,
        action_id,
        action_query,
        action_response,
        original_id,
        action_type,
        table_name,
    ):
        if table_name == "uc_lesson_planner":
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "lesson_plan_main_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_lesson_planner_quick_action").insert(values).execute()
                print("lessonplan response added")
            except Exception as e:
                print(e)

        else:
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "lesson_plan_chat_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_lesson_planner_quick_action").insert(values).execute()
                print("lessonplan response added")
            except Exception as e:
                print(e)

    def add_rubrik_quick_action(
        self,
        action_id,
        action_query,
        action_response,
        original_id,
        action_type,
        table_name,
    ):
        if table_name == "uc_rubrik_generator":
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "rubrik_main_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_rubrik_generator_quick_action").insert(
                    values
                ).execute()
                print("rubrik response added")
            except Exception as e:
                print(e)

        else:
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "rubrik_chat_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_rubrik_generator_quick_action").insert(
                    values
                ).execute()
                print("rubrik response added")
            except Exception as e:
                print(e)

    def add_assesment_quick_action(
        self,
        action_id,
        action_query,
        action_response,
        original_id,
        action_type,
        table_name,
    ):
        if table_name == "uc_assesment_generator":
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "assesment_main_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_assesment_quick_action").insert(values).execute()
                print("assesment response added")
            except Exception as e:
                print(e)

        else:
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "assesment_chat_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_assesment_quick_action").insert(values).execute()
                print("assesment response added")
            except Exception as e:
                print(e)

    def add_diffrentiation_quick_action(
        self,
        action_id,
        action_query,
        action_response,
        original_id,
        action_type,
        table_name,
    ):
        if table_name == "uc_diffrentiation_suggestor":
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "diffrentiation_main_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_diffrentiation_suggestor_quick_action").insert(
                    values
                ).execute()
                print("diffrentiation response added")
            except Exception as e:
                print(e)

        else:
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "diffrentiation_chat_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_diffrentiation_suggestor_quick_action").insert(
                    values
                ).execute()
                print("diffrentiation response added")
            except Exception as e:
                print(e)

    def add_iep_quick_action(
        self,
        action_id,
        action_query,
        action_response,
        original_id,
        action_type,
        table_name,
    ):
        if table_name == "uc_IEP_generator":
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "iep_main_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_IEP_generator_quick_action").insert(values).execute()
                print("iep response added")
            except Exception as e:
                print(e)

        else:
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "iep_chat_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_IEP_generator_quick_action").insert(values).execute()
                print("iep response added")
            except Exception as e:
                print(e)

    def add_unitplan_quick_action(
        self,
        action_id,
        action_query,
        action_response,
        original_id,
        action_type,
        table_name,
    ):
        if table_name == "uc_unit_planner":
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "unitplan_main_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_unit_planner_quick_action").insert(values).execute()
                print("unitplan response added")
            except Exception as e:
                print(e)

        else:
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "unitplan_chat_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_unit_planner_quick_action").insert(values).execute()
                print("unitplan response added")
            except Exception as e:
                print(e)

    def add_feedback_quick_action(
        self,
        action_id,
        action_query,
        action_response,
        original_id,
        action_type,
        table_name,
    ):
        if table_name == "uc_feedback_generator":
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "feedback_generator_main_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_feedback_generator_quick_action").insert(
                    values
                ).execute()
                print("feedback response added")
            except Exception as e:
                print(e)

        else:
            values = {
                "action_id": action_id,
                "action_query": action_query,
                "action_response": action_response,
                "feedback_generator_chat_id": original_id,
                "action_type": action_type,
            }
            try:
                self.db.table("uc_feedback_generator_quick_action").insert(
                    values
                ).execute()
                print("feedback response added")
            except Exception as e:
                print(e)

    def add_diffrentiation(
        self,
        diffrentiation_id,
        user_query,
        diffrentiation_response,
        user_id,
        summary_title,
    ):
        values = {
            "diffrentiation_id": diffrentiation_id,
            "user_query": user_query,
            "diffrentiation_response": diffrentiation_response,
            "user_id": user_id,
            "summary_title": summary_title,
        }
        try:
            self.db.table("uc_diffrentiation_suggestor").insert(values).execute()
            print("assesment response added")
        except Exception as e:
            print(e)

    def add_iep(self, iep_id, user_query, iep_response, user_id, summary_title):
        values = {
            "iep_id": iep_id,
            "user_query": user_query,
            "iep_response": iep_response,
            "user_id": user_id,
            "summary_title": summary_title,
        }
        try:
            self.db.table("uc_IEP_generator").insert(values).execute()
            print("IEP response added")
        except Exception as e:
            print(e)

    def add_feedback(
        self, feedback_id, user_query, feedback_response, user_id, summary_title
    ):
        values = {
            "feedback_id": feedback_id,
            "user_query": user_query,
            "feedback_response": feedback_response,
            "user_id": user_id,
            "summary_title": summary_title,
        }
        try:
            self.db.table("uc_feedback_generator").insert(values).execute()
            print("Feedback response added")
        except Exception as e:
            print(e)

    def add_unitplan(
        self, unitplan_id, user_query, unitplan_response, user_id, summary_title
    ):
        values = {
            "unitplan_id": unitplan_id,
            "user_query": user_query,
            "unitplan_response": unitplan_response,
            "user_id": user_id,
            "summary_title": summary_title,
        }
        try:
            self.db.table("uc_unit_planner").insert(values).execute()
            print("Unit Plan response added")
        except Exception as e:
            print(e)

    def add_chat_history(self, history_id, user_id, summary_title):
        values = {
            "chat_history_id": history_id,
            "user_id": user_id,
            "summary_title": summary_title,
        }
        try:
            self.db.table("uc_chat_history").insert(values).execute()
            print("chat messages added")
        except Exception as e:
            print(e)

    def get_rubrik_by_id_string(self, id) -> str:
        try:
            response = (
                self.db.table("uc_rubrik_generator")
                .select("rubrik_response")
                .eq("rubrik_id", id)
                .execute()
            )
            rubrik_content = response.data[0]["rubrik_response"]

            return rubrik_content
        except Exception as e:
            print(e)
            return None

    def get_interactivechat_by_id_iobytes_object(
        self,
        first_table_name: str,
        second_table_name: str,
        record_id: str,
        id_column_one: str,
        id_column_two: str,
        response_field_one: str,
        response_field_two: str,
        model: Type[BaseModel],
    ) -> Optional[io.BytesIO]:
        try:
            response_first_table_name = (
                self.db.table(first_table_name)
                .select("*")
                .eq(id_column_one, record_id)
                .order("created_at")
                .execute()
            )
            # print("response_first_table_name - ", response_first_table_name)
            response_second_table_name = (
                self.db.table(second_table_name)
                .select("*")
                .eq(id_column_two, record_id)
                .order("created_at")
                .execute()
            )
            # print("response_second_table_name - ", response_second_table_name)
            if response_first_table_name.data != []:
                final_response = model(
                    response=response_first_table_name.data[0][response_field_one],
                    table_name=first_table_name,
                )

            else:
                final_response = model(
                    response=response_second_table_name.data[0][response_field_two],
                    table_name=second_table_name,
                )
            bytes_io = io.BytesIO()
            bytes_io.write(final_response.response.encode("utf-8"))
            bytes_io.seek(0)
            return bytes_io

        except Exception as e:
            print(e)
            return None

    def get_assesment_by_id_string(self, id) -> str:
        try:
            response = (
                self.db.table("uc_assesment_generator")
                .select("assesment_response")
                .eq("assessment_id", id)
                .execute()
            )
            assesment_content = response.data[0]["assesment_response"]
            return assesment_content

        except Exception as e:
            print(e)
            return None

    def get_response_by_id(self, id, agent_details: dict) -> Optional[bytes]:
        try:
            table_name = agent_details["table_name_one"]
            response_field = agent_details["response_field_one"]
            id_column = agent_details["id_column_one"]

            response = (
                self.db.table(table_name)
                .select(response_field)
                .eq(id_column, id)
                .execute()
            )
            response_content = response.data[0][response_field]

            bytes_io = io.BytesIO()

            # Write the encoded string to the BytesIO object
            bytes_io.write(response_content.encode("utf-8"))

            # Move the file pointer to the beginning
            bytes_io.seek(0)

            # Read the bytes from the BytesIO object
            response_bytes = bytes_io.read()

            # Close the BytesIO object
            bytes_io.close()
            return response_bytes

        except Exception as e:
            print(e)
            return None

    def get_unitplan_by_id_string(self, id) -> Optional[io.BytesIO]:
        try:
            response = (
                self.db.table("uc_unit_planner")
                .select("unitplan_response")
                .eq("unitplan_id", id)
                .execute()
            )
            unitplan_content = response.data[0]["unitplan_response"]
            return unitplan_content

        except Exception as e:
            print(e)
            return None

    def get_iep_by_id_string(self, id) -> Optional[io.BytesIO]:
        try:
            response = (
                self.db.table("uc_IEP_generator")
                .select("iep_response")
                .eq("iep_id", id)
                .execute()
            )
            iep_content = response.data[0]["iep_response"]
            return iep_content

        except Exception as e:
            print(e)
            return None

    def get_feedback_by_id_string(self, id) -> Optional[io.BytesIO]:
        try:
            response = (
                self.db.table("uc_feedback_generator")
                .select("feedback_response")
                .eq("feedback_id", id)
                .execute()
            )
            feedback_content = response.data[0]["feedback_response"]
            return feedback_content

        except Exception as e:
            print(e)
            return None

    def get_diffrentiation_by_id_string(self, id) -> str:
        try:
            response = (
                self.db.table("uc_diffrentiation_suggestor")
                .select("diffrentiation_response")
                .eq("diffrentiation_id", id)
                .execute()
            )
            diffrentiation_content = response.data[0]["diffrentiation_response"]
            return diffrentiation_content

        except Exception as e:
            print(e)
            return None

    def fetch_by_id_iobytes_object(
        self,
        first_table_name: str,
        second_table_name: str,
        third_tabel_name: str,
        record_id: str,
        id_column_one: str,
        id_column_two: str,
        response_field_one: str,
        response_field_two: str,
        response_field_three: str,
        model: Type[BaseModel],
    ) -> Optional[io.BytesIO]:
        try:
            response_first_table_name = (
                self.db.table(first_table_name)
                .select("*")
                .eq(id_column_one, record_id)
                .order("created_at")
                .execute()
            )
            # print("response_first_table_name - ", response_first_table_name)
            response_second_table_name = (
                self.db.table(second_table_name)
                .select("*")
                .eq(id_column_two, record_id)
                .order("created_at")
                .execute()
            )
            response_third_table_name = (
                self.db.table(third_tabel_name)
                .select("*")
                .eq("action_id", record_id)
                .order("created_at")
                .execute()
            )
            # print("response_second_table_name - ", response_second_table_name)
            if response_first_table_name.data != []:
                final_response = model(
                    response=response_first_table_name.data[0][response_field_one],
                    table_name=first_table_name,
                )

            elif response_second_table_name.data != []:
                final_response = model(
                    response=response_second_table_name.data[0][response_field_two],
                    table_name=second_table_name,
                )
            else:
                final_response = model(
                    response=response_third_table_name.data[0][response_field_three],
                    table_name=third_tabel_name,
                )

            bytes_io = io.BytesIO()
            bytes_io.write(final_response.response.encode("utf-8"))
            bytes_io.seek(0)
            return bytes_io
        except Exception as e:
            print(f"Exception occurred while fetching data from table: {str(e)}")
            return None

    def get_lesson_plan_by_id_string(self, id) -> str:
        try:
            response = (
                self.db.table("uc_lesson_planner")
                .select("lesson_plan")
                .eq("lesson_plan_id", id)
                .execute()
            )
            lesson_plan_content = response.data[0]["lesson_plan"]
            return lesson_plan_content

        except Exception as e:
            print(e)
            return None

    def fetch_cleaned_data(
        self, user_id: str
    ) -> Optional[List[CleanedHistoryResponse]]:
        try:
            # Extract query data from uc_chat_history table
            response = (
                self.db.table("uc_chat_history")
                .select("chat_history_id, edited_title, summary_title, favorite")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )

            clean_response = [
                CleanedHistoryResponse(
                    chat_history_id=item["chat_history_id"],
                    user_query=item["edited_title"]
                    if item["edited_title"]
                    else item["summary_title"],
                    is_favorite=item["favorite"],
                )
                for item in response.data
            ]
            return clean_response

        except Exception as e:
            print(f"An error occurred while fetching and cleaning data: {str(e)}")
            return None

    def fetch_session_id(self, chat_msg_id: str):
        try:
            response = (
                self.db.table("uc_chat_msg")
                .select("history_id")
                .eq("chat_msg_id", chat_msg_id)
                .execute()
            )
            response_data = response.data[0]["history_id"]

            return response_data
        except Exception as e:
            print(f"An error occurred while fetching session id: {str(e)}")
            return None

    def return_data_for_url(
        self, id: str, source: str
    ) -> List[Union[AgentMainItem, ChatHistoryListItem]]:
        try:
            response = (
                self.db.table("uc_share_url_data")
                .select("response_data")
                .match({"response_id": id, "source": source})
                .execute()
            )

            response_data = response.data[0]["response_data"]

            # Deserialize JSON string to a list of dictionaries
            data_list = json.loads(response_data)
            if source == "ai_coach":
                # Convert each dictionary to a Pydantic instance
                pydantic_list = [ChatHistoryListItem(**item) for item in data_list]
                return pydantic_list
            else:
                # Create an empty list to store the Pydantic instances
                pydantic_list = []

                # Iterate through each dictionary and instantiate the appropriate Pydantic model
                for item in data_list:
                    if item["message_type"] == "main_content":
                        pydantic_instance = AgentMainItem(**item)
                        pydantic_list.append(pydantic_instance)
                    else:
                        pydantic_instance = ChatHistoryListItem(**item)
                        pydantic_list.append(pydantic_instance)
                return pydantic_list
        except Exception as e:
            print(f"An error occurred while fetching data for share url: {str(e)}")
            return None

    def get_chat_history_list(
        self, history_id: str
    ) -> Optional[List[ChatHistoryListItem]]:
        try:
            # Fetch data from Supabase
            response = (
                self.db.table("uc_chat_msg")
                .select("chat_msg_id, created_at, user_query, coach_response")
                .eq("history_id", history_id)
                .order("created_at")
                .execute()
            )

            # Extract response data
            response_data = response.data

            # Prepare to collect all actions
            all_actions = []

            # Fetch actions related to each message
            for message in response_data:
                chat_msg_id = message["chat_msg_id"]
                response2 = (
                    self.db.table("uc_chat_quick_action")
                    .select(
                        "action_id, created_at, action_query, action_response, chat_msg_id"
                    )
                    .eq("chat_msg_id", chat_msg_id)
                    .execute()
                )
                all_actions.extend(response2.data)

            # Combine and sort messages and actions by created_at
            combined_data = []

            for message in response_data:
                combined_data.append(
                    {
                        "type": "message",
                        "id": message["chat_msg_id"],
                        "created_at": parser.isoparse(message["created_at"]),
                        "user_query": message["user_query"],
                        "response": message["coach_response"],
                    }
                )

            for action in all_actions:
                combined_data.append(
                    {
                        "type": "action",
                        "id": action["action_id"],
                        "created_at": parser.isoparse(action["created_at"]),
                        "chat_msg_id": action["chat_msg_id"],
                        "user_query": action["action_query"],
                        "response": action["action_response"],
                    }
                )

            # Sort combined data by created_at
            combined_data.sort(key=lambda x: x["created_at"])

            wrapped_data = []
            for item in combined_data:
                wrapped_data.append(
                    ChatHistoryListItem(
                        message_type=item["type"],
                        id=item["id"],
                        created_at=item["created_at"],
                        user_query=item["user_query"],
                        coach_response=item["response"],
                    )
                )

            return wrapped_data

        except Exception as e:
            print(f"An error occurred while fetching chat history list: {str(e)}")
            return []

    def get_interactive_chat_history_list_for_share(self, history_id: str) -> List:
        try:
            # Fetch data from Supabase
            response = (
                self.db.table("uc_chat_msg")
                .select("chat_msg_id, created_at, user_query, coach_response")
                .eq("history_id", history_id)
                .order("created_at")
                .execute()
            )

            # Extract response data
            response_data = response.data

            # Prepare to collect all actions
            all_actions = []

            # Fetch actions related to each message
            for message in response_data:
                chat_msg_id = message["chat_msg_id"]
                response2 = (
                    self.db.table("uc_chat_quick_action")
                    .select(
                        "action_id, created_at, action_query, action_response, chat_msg_id"
                    )
                    .eq("chat_msg_id", chat_msg_id)
                    .execute()
                )
                all_actions.extend(response2.data)

            # Combine and sort messages and actions by created_at
            combined_data = []

            for message in response_data:
                combined_data.append(
                    {
                        "type": "message",
                        "id": message["chat_msg_id"],
                        "created_at": parser.isoparse(message["created_at"]),
                        "user_query": message["user_query"],
                        "response": message["coach_response"],
                    }
                )

            for action in all_actions:
                combined_data.append(
                    {
                        "type": "action",
                        "id": action["action_id"],
                        "created_at": parser.isoparse(action["created_at"]),
                        "chat_msg_id": action["chat_msg_id"],
                        "user_query": action["action_query"],
                        "response": action["action_response"],
                    }
                )

            # Sort combined data by created_at
            combined_data.sort(key=lambda x: x["created_at"])

            return combined_data

        except Exception as e:
            print(f"An error occurred while fetching chat history list: {str(e)}")
            return []

    def setup_to_edit(self, history_id: str, user_msg: str):
        try:
            updated_response = (
                self.db.table("uc_chat_history")
                .update({"edited_title": user_msg})
                .eq("chat_history_id", history_id)
                .execute()
            )

            result = updated_response.data[0]["edited_title"]

            if result:
                print("user query  updated successfully!")
            else:
                print("Failed to update user query.")
            return result

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def title_edit(self, agent_id: str, user_msg: str, agent_details: dict):
        try:
            table_name = agent_details["table_name_one"]
            id_column = agent_details["id_column_one"]

            updated_response = (
                self.db.table(table_name)
                .update({"edited_title": user_msg})
                .eq(id_column, agent_id)
                .execute()
            )

            result = updated_response.data[0]["edited_title"]

            if result:
                print("user query  updated successfully!")
            else:
                print("Failed to update user query.")
            return result

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def store_edited_response(self, chat_id: str, user_msg: str, coach_response: str):
        try:
            updated_response = (
                self.db.table("uc_chat_msg")
                .update({"user_query": user_msg, "coach_response": coach_response})
                .eq("chat_msg_id", chat_id)
                .execute()
            )

            result = updated_response.data

            if result:
                print("user query and response updated successfully!")
            else:
                print("Failed to update user query and response.")

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def store_edited_response_diffrentiation_chat(
        self, chat_id: str, user_msg: str, chat_response: str
    ):
        try:
            updated_response = (
                self.db.table("uc_diffrentiation_chat")
                .update({"user_query": user_msg, "chat_response": chat_response})
                .eq("chat_msg_id", chat_id)
                .execute()
            )

            result = updated_response.data

            if result:
                print("user query and response updated successfully!")
            else:
                print("Failed to update user query and response.")

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def store_edited_response_unitplan_chat(
        self, chat_id: str, user_msg: str, chat_response: str
    ):
        try:
            updated_response = (
                self.db.table("uc_unitplan_chat")
                .update({"user_query": user_msg, "chat_response": chat_response})
                .eq("chat_msg_id", chat_id)
                .execute()
            )

            result = updated_response.data

            if result:
                print("user query and response updated successfully!")
            else:
                print("Failed to update user query and response.")

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def store_edited_response_iep_chat(
        self, chat_id: str, user_msg: str, chat_response: str
    ):
        try:
            updated_response = (
                self.db.table("uc_IEP_chat")
                .update({"user_query": user_msg, "chat_response": chat_response})
                .eq("chat_msg_id", chat_id)
                .execute()
            )

            result = updated_response.data

            if result:
                print("user query and response updated successfully!")
            else:
                print("Failed to update user query and response.")

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def store_edited_response_feedback_chat(
        self, chat_id: str, user_msg: str, chat_response: str
    ):
        try:
            updated_response = (
                self.db.table("uc_feedback_generator_chat")
                .update({"user_query": user_msg, "chat_response": chat_response})
                .eq("chat_msg_id", chat_id)
                .execute()
            )

            result = updated_response.data

            if result:
                print("user query and response updated successfully!")
            else:
                print("Failed to update user query and response.")

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def store_edited_response_assessment_chat(
        self, chat_id: str, user_msg: str, chat_response: str
    ):
        try:
            updated_response = (
                self.db.table("uc_assesment_chat")
                .update({"user_query": user_msg, "chat_response": chat_response})
                .eq("chat_msg_id", chat_id)
                .execute()
            )

            result = updated_response.data

            if result:
                print("user query and response updated successfully!")
            else:
                print("Failed to update user query and response.")

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def store_edited_response_lesson_plan_chat(
        self, chat_id: str, user_msg: str, chat_response: str
    ):
        try:
            updated_response = (
                self.db.table("uc_lesson_planner_chat")
                .update({"user_query": user_msg, "chat_response": chat_response})
                .eq("chat_msg_id", chat_id)
                .execute()
            )

            result = updated_response.data

            if result:
                print("user query and response updated successfully!")
            else:
                print("Failed to update user query and response.")

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def store_edited_response_rubrk_chat(
        self, chat_id: str, user_msg: str, chat_response: str
    ):
        try:
            updated_response = (
                self.db.table("uc_rubrik_chat")
                .update({"user_query": user_msg, "chat_response": chat_response})
                .eq("chat_msg_id", chat_id)
                .execute()
            )

            result = updated_response.data

            if result:
                print("user query and response updated successfully!")
            else:
                print("Failed to update user query and response.")

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def update_feedback_intreactive_chat(
        self, chat_msg_id: str, feedback: str, feedback_des: str
    ):
        try:
            # Update the feedback and feedback_description in the database
            response = (
                self.db.table("uc_chat_msg")
                .update({"feedback": feedback, "feedback_description": feedback_des})
                .eq("chat_msg_id", chat_msg_id)
                .execute()
            )
            result = response.data
            if not result:
                response_two = (
                    self.db.table("uc_chat_quick_action")
                    .update(
                        {"feedback": feedback, "feedback_description": feedback_des}
                    )
                    .eq("action_id", chat_msg_id)
                    .execute()
                )
                result = response_two.data

            # Check if the update was successful
            if result:
                print("Feedback updated successfully!")
            else:
                print("Failed to update feedback.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def update_response_data_of_share_link(
        self, id: str, source: str, response_data: List[dict]
    ):
        try:
            # Update the feedback and feedback_description in the database
            response = (
                self.db.table("uc_share_url_data")
                .update({"response_data": response_data})
                .match({"response_id": id, "source": source})
                .execute()
            )

            result = response.data

            # Check if the update was successful
            if result:
                print("Respone data of share link updated successfully!")
            else:
                print("Failed to update response data of share link.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def delete_history_intreactive_chat(self, history_id: str):
        try:
            # delete the chat history in the database
            self.db.table("uc_chat_msg").delete().eq("history_id", history_id).execute()

            response = (
                self.db.table("uc_chat_history")
                .delete()
                .eq("chat_history_id", history_id)
                .execute()
            )

            # Check if the delete was successful
            if response:
                print("deleted chat history successfully!")
            else:
                print("Failed to delete chat history.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def delete_history_chat(self, history_id: str, agent_details: dict):
        try:
            table_one = agent_details["table_name_one"]
            table_two = agent_details["table_name_two"]
            table_three = agent_details["table_name_three"]
            main_id_reference = agent_details["main_id_reference"]
            id_column = agent_details["id_column_one"]
            quick_action_main_id = agent_details["quick_action_main_id_link"]

            # Delete in the quick action table first if present
            self.db.table(table_three).delete().eq(
                quick_action_main_id, history_id
            ).execute()

            # Delete the chat history in the chat table database
            self.db.table(table_two).delete().eq(
                main_id_reference, history_id
            ).execute()

            # Then delete in the main table
            self.db.table(table_one).delete().eq(id_column, history_id).execute()

        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def get_id_list(
        self, user_id: str, table_name: str, id_column: str
    ) -> Optional[List[IDList]]:
        try:
            # Fetch the latest created_at date
            latest_date_response = (
                self.db.table(table_name)
                .select("created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            # Get the latest created_at date
            latest_created_at = latest_date_response.data[0]["created_at"]
            print("latest_created_at ------ ", latest_created_at)
            # Convert the latest_created_at to a datetime object
            latest_created_at_datetime = parser.isoparse(latest_created_at)
            print("latest_created_at_datetime -------", latest_created_at_datetime)
            # Calculate the date 30 days before the latest created_at date
            thirty_days_before_latest = (
                latest_created_at_datetime - timedelta(days=30)
            ).isoformat()
            print("thirty_days_before_latest --------", thirty_days_before_latest)
            # Fetch data from Supabase
            response = (
                self.db.table(table_name)
                .select(f"{id_column}, summary_title, edited_title, created_at")
                .eq("user_id", user_id)
                .gte("created_at", thirty_days_before_latest)
                .order("created_at", desc=True)
                .execute()
            )

            # Extract response data
            response_data = response.data

            # Create a list of ChatHistoryListItem objects
            id_list = [
                IDList(
                    agent_id=item[id_column],
                    date=item["created_at"],
                    user_query_title=item["edited_title"]
                    if item["edited_title"]
                    else item["summary_title"],
                )
                for item in response_data
            ]

            return id_list
        except Exception as e:
            print(f"An error occurred while fetching the history list: {str(e)}")
            return []

    def get_response_title(self, agent_id: str, agent_details: dict):
        try:
            table_name = agent_details["table_name_one"]
            id_column = agent_details["id_column_one"]

            if table_name != "uc_chat_msg":
                response = (
                    self.db.table(table_name)
                    .select(f"{id_column}, summary_title, edited_title")
                    .eq(f"{id_column}", agent_id)
                    .execute()
                )

            else:
                response = (
                    self.db.table(table_name)
                    .select(f"{id_column}")
                    .eq(f"{id_column}", agent_id)
                    .execute()
                )

            response_data = response.data
            entry = response_data[0]

            if table_name != "uc_chat_msg":
                # Determine the response title based on the presence of edited_title
                response_title = (
                    entry["edited_title"]
                    if entry["edited_title"]
                    else entry["summary_title"]
                )

            else:
                response_title = "Chat Message"
            return response_title

        except Exception as e:
            print(f"An error occurred while fetching the history list: {str(e)}")
            return []

    def get_agent_plan(
        self, agent_id: str, agent_details: dict
    ) -> List[Union[AgentMainItem, ChatHistoryListItem]]:
        try:
            table_one = agent_details["table_name_one"]
            table_two = agent_details["table_name_two"]
            table_three = agent_details["table_name_three"]
            id_column_one = agent_details["id_column_one"]
            response_field = agent_details["response_field_one"]
            main_id_reference = agent_details["main_id_reference"]
            quick_action_main_id = agent_details["quick_action_main_id_link"]
            quick_action_chat_id = agent_details["quick_action_chat_id_link"]
            # Fetch data from Supabase
            response_agent = (
                self.db.table(table_one)
                .select(f"{id_column_one}, {response_field}, created_at")
                .eq(id_column_one, agent_id)
                .order("created_at")
                .execute()
            )

            response_agent_data = response_agent.data

            response_chat = (
                self.db.table(table_two)
                .select("chat_msg_id, user_query, chat_response, created_at")
                .eq(main_id_reference, agent_id)
                .order("created_at")
                .execute()
            )

            response_chat_data = response_chat.data
            # Prepare to collect all actions
            all_actions = []

            # Fetch actions related to each message
            for message in response_chat_data:
                chat_msg_id = message["chat_msg_id"]
                response_quick_action_1 = (
                    self.db.table(table_three)
                    .select("action_id, created_at, action_query, action_response")
                    .eq(f"{quick_action_chat_id}", chat_msg_id)
                    .order("created_at")
                    .execute()
                )
                all_actions.extend(response_quick_action_1.data)

            response_quick_action_2 = (
                self.db.table(table_three)
                .select("action_id, created_at, action_query, action_response")
                .eq(f"{quick_action_main_id}", agent_id)
                .order("created_at")
                .execute()
            )

            all_actions.extend(response_quick_action_2.data)

            # Combine messages and actions
            combined_data = []

            combined_data.append(
                {
                    "type": "main_content",
                    "id": agent_id,
                    "created_at": parser.isoparse(response_agent_data[0]["created_at"]),
                    "response": response_agent_data[0][f"{response_field}"],
                }
            )

            for message in response_chat_data:
                combined_data.append(
                    {
                        "type": "message",
                        "id": message["chat_msg_id"],
                        "created_at": parser.isoparse(message["created_at"]),
                        "user_query": message["user_query"],
                        "response": message["chat_response"],
                    }
                )

            for action in all_actions:
                combined_data.append(
                    {
                        "type": "action",
                        "id": action["action_id"],
                        "created_at": parser.isoparse(action["created_at"]),
                        "user_query": action["action_query"],
                        "response": action["action_response"],
                    }
                )

            # Sort combined data by created_at
            combined_data.sort(key=lambda x: x["created_at"])

            # Wrap data with Pydantic models
            wrapped_data = []
            for item in combined_data:
                if item["type"] == "main_content":
                    wrapped_data.append(
                        AgentMainItem(
                            message_type=item["type"],
                            id=item["id"],
                            created_at=item["created_at"],
                            coach_response=item["response"],
                        )
                    )
                else:
                    wrapped_data.append(
                        ChatHistoryListItem(
                            message_type=item["type"],
                            id=item["id"],
                            created_at=item["created_at"],
                            user_query=item["user_query"],
                            coach_response=item["response"],
                        )
                    )

            return wrapped_data
        except Exception as e:
            print(f"An error occurred while fetching plan: {str(e)}")
            return []

    def get_context_list(
        self, agent_id: str, agent_details: dict
    ) -> List[dict]:  # Now returning List of dictionaries
        try:
            table_one = agent_details["table_name_one"]
            table_two = agent_details["table_name_two"]
            table_three = agent_details["table_name_three"]
            id_column_one = agent_details["id_column_one"]
            response_field = agent_details["response_field_one"]
            main_id_reference = agent_details["main_id_reference"]
            quick_action_main_id = agent_details["quick_action_main_id_link"]
            quick_action_chat_id = agent_details["quick_action_chat_id_link"]

            # Fetch data from Supabase
            response_agent = (
                self.db.table(table_one)
                .select(f"{id_column_one}, {response_field}, created_at")
                .eq(id_column_one, agent_id)
                .order("created_at")
                .execute()
            )

            response_agent_data = response_agent.data
            # Ensure that there is data for the agent response
            if not response_agent_data:
                return []

            response_chat = (
                self.db.table(table_two)
                .select("chat_msg_id, user_query, chat_response, created_at")
                .eq(main_id_reference, agent_id)
                .order("created_at")
                .execute()
            )

            response_chat_data = response_chat.data

            # Prepare to collect all actions
            all_actions = []

            # Fetch actions related to each message
            for message in response_chat_data:
                chat_msg_id = message["chat_msg_id"]
                response_quick_action_1 = (
                    self.db.table(table_three)
                    .select("action_id, created_at, action_query, action_response")
                    .eq(f"{quick_action_chat_id}", chat_msg_id)
                    .order("created_at")
                    .execute()
                )
                all_actions.extend(response_quick_action_1.data)

            response_quick_action_2 = (
                self.db.table(table_three)
                .select("action_id, created_at, action_query, action_response")
                .eq(f"{quick_action_main_id}", agent_id)
                .order("created_at")
                .execute()
            )

            all_actions.extend(response_quick_action_2.data)

            # Combine messages and actions
            combined_data = []

            # Add quick actions for both chat messages and main response
            for action in all_actions:
                user_action = {
                    "role": "user",
                    "content": action["action_query"],
                    "created_at": parser.isoparse(action["created_at"]),
                }
                assistant_action = {
                    "role": "assistant",
                    "content": action["action_response"],
                    "created_at": parser.isoparse(action["created_at"]),
                }
                combined_data.append((user_action, assistant_action))

            # Sort combined_data by created_at for the tuples
            combined_data.sort(key=lambda x: x[0]["created_at"])

            # Now handle wrapping for combined_data (which only contains tuples)
            wrapped_data = []
            for action_tuple in combined_data:
                wrapped_data.append(
                    (
                        {
                            "role": action_tuple[0]["role"],
                            "content": action_tuple[0]["content"],
                        },
                        {
                            "role": action_tuple[1]["role"],
                            "content": action_tuple[1]["content"],
                        },
                    )
                )

            # Add agent's main response as the first element of wrapped_data (without created_at)
            wrapped_data.insert(
                0,
                {
                    "role": "assistant",
                    "content": response_agent_data[0][f"{response_field}"],
                },
            )

            return wrapped_data
        except Exception as e:
            print(f"An error occurred while fetching plan: {str(e)}")
            return []

    def update_feedback(
        self, iep_id: str, feedback: str, feedback_description: str, agent_details: dict
    ):
        try:
            table_name = agent_details["table_name_one"]
            id_column = agent_details["id_column_one"]
            table_name_two = agent_details["table_name_two"]
            id_column_two = agent_details["id_column_two"]
            table_name_three = agent_details["table_name_three"]

            # Update the feedback and feedback_description in the database
            response = (
                self.db.table(table_name)
                .update(
                    {"feedback": feedback, "feedback_description": feedback_description}
                )
                .eq(id_column, iep_id)
                .execute()
            )
            result = response.data
            if not result:
                response_two = (
                    self.db.table(table_name_two)
                    .update(
                        {
                            "feedback": feedback,
                            "feedback_description": feedback_description,
                        }
                    )
                    .eq(id_column_two, iep_id)
                    .execute()
                )
                result = response_two.data
            if not result:
                response_three = (
                    self.db.table(table_name_three)
                    .update(
                        {
                            "feedback": feedback,
                            "feedback_description": feedback_description,
                        }
                    )
                    .eq("action_id", iep_id)
                    .execute()
                )
                result = response_three.data

            # Check if the update was successful
            if result:
                print("Feedback updated successfully!")
            else:
                print("Failed to update feedback.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def add_expanded_response(self, id, expanded_response, user_query):
        values = {
            "request_id": id,
            "expanded_msg": expanded_response,
            "user_query": user_query,
        }
        try:
            self.db.table("uc_bots_expanded").insert(values).execute()
            print("expanded response added")
        except Exception as e:
            print(e)

    def fetch_lesson_plan_response_data(self, user_id: str) -> GenerateLessonPlan:
        try:
            # Fetch the latest lesson_plan_id
            latest_lesson_response = (
                self.db.table("uc_lesson_planner")
                .select("lesson_plan_id, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            lesson_plan_id = latest_lesson_response.data[0]["lesson_plan_id"]
            response = (
                self.db.table("uc_lesson_planner")
                .select("user_query")
                .eq("lesson_plan_id", lesson_plan_id)
                .execute()
            )
            user_query = response.data[0]["user_query"]

            # Extract data from user_query
            grade = user_query.split("Grade:")[1].split("Topic:")[0].strip()
            topic = (
                user_query.split("Topic:")[1].split("Additional Critieria")[0].strip()
            )
            additional_criteria = (
                user_query.split("Additional Critieria:")[1]
                .split("Standards to align to")[0]
                .strip()
            )
            standards_to_align_to = user_query.split("Standards to align to:")[
                1
            ].strip()

            # Create instance of LessonPlanEditInput
            lesson_plan_data = GenerateLessonPlan(
                grade_level=grade,
                topic=topic,
                additional_criteria=additional_criteria,
                standards=standards_to_align_to,
            )
            return lesson_plan_data

        except Exception as e:
            print(f"An error occurred while fetching lesson plan input data: {str(e)}")
            return None

    def fetch_assessment_response_data(
        self, user_id: str
    ) -> Union[GenerateAssessmentEdit, GenerateAssessment]:
        try:
            # Fetch the latest assesment_id
            latest_assesment_response = (
                self.db.table("uc_assesment_generator")
                .select("assessment_id, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            assessment_id = latest_assesment_response.data[0]["assessment_id"]
            response = (
                self.db.table("uc_assesment_generator")
                .select("user_query")
                .eq("assessment_id", assessment_id)
                .execute()
            )
            user_query = response.data[0]["user_query"]

            # Extract data from user_query
            subject = user_query.split("Subject:")[1].split("Grade:")[0].strip()
            grade = user_query.split("Grade:")[1].split("Topic:")[0].strip()
            topic = user_query.split("Topic:")[1].split("Standards:")[0].strip()
            standard = (
                user_query.split("Standards:")[1]
                .split("Preferred Assessment Type:")[0]
                .strip()
            )
            preferred_assessment_type = user_query.split("Preferred Assessment Type:")[
                1
            ].strip()
            if "Quiz" in preferred_assessment_type:
                # Split the string into "Quiz" and the remaning part
                parts = preferred_assessment_type.split("Quiz", 1)
                preferred_assessment_type = "Quiz".strip()
                assesment_type_two = parts[1].strip()

                # Create instance of AssessmentEditInput
                assessment_plan_data = GenerateAssessmentEdit(
                    subject=subject,
                    grade=grade,
                    skills=topic,
                    learning_objectives=standard,
                    assesment_type=preferred_assessment_type,
                    assesment_type_two=assesment_type_two,
                )
                return assessment_plan_data
            # Create instance of AssessmentEditInput
            assessment_plan_data = GenerateAssessment(
                subject=subject,
                grade=grade,
                skills=topic,
                learning_objectives=standard,
                assesment_type=preferred_assessment_type,
            )
            return assessment_plan_data

        except Exception as e:
            print(
                f"An error occurred while fetching assessment plan input data: {str(e)}"
            )
            return None

    def fetch_diffrentiation_response_data(
        self, user_id: str
    ) -> GenerateDiffrentiation:
        try:
            # Fetch the latest diffrentiation_id
            latest_diffrentiation_response = (
                self.db.table("uc_diffrentiation_suggestor")
                .select("diffrentiation_id, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            diffrentiation_id = latest_diffrentiation_response.data[0][
                "diffrentiation_id"
            ]
            response = (
                self.db.table("uc_diffrentiation_suggestor")
                .select("user_query")
                .eq("diffrentiation_id", diffrentiation_id)
                .execute()
            )
            user_query = response.data[0]["user_query"]

            # Extract data from user_query
            grade = user_query.split("Grade:")[1].split("Subject/Topic:")[0].strip()
            lesson_plan = (
                user_query.split("Subject/Topic:")[1].split("Standards:")[0].strip()
            )
            desired_outcomes = (
                user_query.split("Standards:")[1]
                .split("Proficiency of students:")[0]
                .strip()
            )
            learning_profiles = (
                user_query.split("Proficiency of students:")[1]
                .split("Differentiation Type:")[0]
                .strip()
            )
            diffrentiation_types = (
                user_query.split("Differentiation Type:")[1]
                .split("Assessment type:")[0]
                .strip()
            )

            # Create instance of DiffrentiationEditInput
            diffrentiation_plan_data = GenerateDiffrentiation(
                grade=grade,
                desired_outcomes=desired_outcomes,
                lesson_plan=lesson_plan,
                diffrentiation_types=diffrentiation_types,
                learning_profiles=learning_profiles,
            )
            return diffrentiation_plan_data

        except Exception as e:
            print(
                f"An error occurred while fetching diffrentiation plan input data: {str(e)}"
            )
            return None

    def fetch_rubrics_response_data(self, user_id: str) -> GenerateRubrik:
        try:
            # Fetch the latest diffrentiation_id
            latest_rubrics_response = (
                self.db.table("uc_rubrik_generator")
                .select("rubrik_id, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            rubrik_id = latest_rubrics_response.data[0]["rubrik_id"]
            response = (
                self.db.table("uc_rubrik_generator")
                .select("user_query")
                .eq("rubrik_id", rubrik_id)
                .execute()
            )
            user_query = response.data[0]["user_query"]

            # Extract data from user_query
            project_description = (
                user_query.split("Project Description:")[1]
                .split("Evaluation Criteria:")[0]
                .strip()
            )
            evaluation_criteria = (
                user_query.split("Evaluation Criteria:")[1]
                .split("Level of Achievement:")[0]
                .strip()
            )
            level_of_achievement = (
                user_query.split("Level of Achievement:")[1]
                .split("Standards Alignment:")[0]
                .strip()
            )
            standards_alignment = (
                user_query.split("Standards Alignment:")[1]
                .split("Flexibility Needs:")[0]
                .strip()
            )
            flexibility_needs = user_query.split("Flexibility Needs:")[1].strip()

            # Create instance of RubricsEditInput
            rubrics_plan_data = GenerateRubrik(
                project_description=project_description,
                evaluation_criteria=evaluation_criteria,
                level_of_achievement=level_of_achievement,
                standards_alignment=standards_alignment,
                flexibility_needs=flexibility_needs,
            )
            return rubrics_plan_data

        except Exception as e:
            print(f"An error occurred while fetching rubrics plan input data: {str(e)}")
            return None

    def fetch_iep_response_data(self, user_id: str) -> GenerateIEP:
        try:
            # Fetch the latest diffrentiation_id
            latest_iep_response = (
                self.db.table("uc_IEP_generator")
                .select("iep_id, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            iep_id = latest_iep_response.data[0]["iep_id"]
            response = (
                self.db.table("uc_IEP_generator")
                .select("user_query")
                .eq("iep_id", iep_id)
                .execute()
            )
            user_query = response.data[0]["user_query"]

            # Extract data from user_query
            grade = user_query.split("Grade:")[1].split("Date of Birth:")[0].strip()
            date_of_birth = (
                user_query.split("Date of Birth:")[1].split("Eligibility:")[0].strip()
            )
            eligibility = (
                user_query.split("Eligibility:")[1]
                .split("People Providing Services")[0]
                .strip()
            )
            people_providing_services = (
                user_query.split("People Providing Services")[1]
                .split("Parent Feedback:")[0]
                .strip()
            )
            parent_feedback = (
                user_query.split("Parent Feedback:")[1]
                .split("Teacher Feedback:")[0]
                .strip()
            )
            teacher_feedback = (
                user_query.split("Teacher Feedback:")[1]
                .split("Academic Performance:")[0]
                .strip()
            )
            academic_performance = (
                user_query.split("Academic Performance:")[1]
                .split("Functional Performance:")[0]
                .strip()
            )
            functional_performance = (
                user_query.split("Functional Performance:")[1]
                .split("Strengths:")[0]
                .strip()
            )
            strengths = user_query.split("Strengths:")[1].split("Needs:")[0].strip()
            needs = (
                user_query.split("Needs:")[1]
                .split("Services Provided & Service Delivery:")[0]
                .strip()
            )
            services_provided = (
                user_query.split("Services Provided & Service Delivery:")[1]
                .split("Postsecondary Goals:")[0]
                .strip()
            )
            postsecondary_goals = user_query.split("Postsecondary Goals:")[1].strip()

            # Create instance of IEPEditInput
            iep_plan_data = GenerateIEP(
                grade=grade,
                date_of_birth=date_of_birth,
                eligibility=eligibility,
                people_providing_services=people_providing_services,
                parent_feedback=parent_feedback,
                teacher_feedback=teacher_feedback,
                academic_performance=academic_performance,
                functional_performance=functional_performance,
                strengths=strengths,
                needs=needs,
                services_provided=services_provided,
                postsecondary_goals=postsecondary_goals,
            )
            return iep_plan_data

        except Exception as e:
            print(
                f"An error occurred while fetching diffrentiation plan input data: {str(e)}"
            )
            return

    def fetch_unitplan_response_data(self, user_id: str) -> GenerateUnitPlan:
        try:
            # Fetch the latest diffrentiation_id
            latest_unitplan_response = (
                self.db.table("uc_unit_planner")
                .select("unitplan_id, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            unitplan_id = latest_unitplan_response.data[0]["unitplan_id"]
            response = (
                self.db.table("uc_unit_planner")
                .select("user_query")
                .eq("unitplan_id", unitplan_id)
                .execute()
            )
            user_query = response.data[0]["user_query"]

            # Extract data from user_query
            grade = user_query.split("Grade:")[1].split("Unit Title:")[0].strip()
            unit_title = user_query.split("Unit Title:")[1].split("Subject:")[0].strip()
            subject = (
                user_query.split("Subject:")[1].split("Unit Objectives:")[0].strip()
            )
            unit_objectives = (
                user_query.split("Unit Objectives:")[1].split("Standard:")[0].strip()
            )
            standard = (
                user_query.split("Standard:")[1].split("Length of a Unit:")[0].strip()
            )
            length_of_a_unit = (
                user_query.split("Length of a Unit:")[1]
                .split("Assessment Strategies:")[0]
                .strip()
            )
            assessment_strategies = (
                user_query.split("Assessment Strategies:")[1]
                .split("Interdisciplinary Links:")[0]
                .strip()
            )
            interdisciplinary_links = (
                user_query.split("Interdisciplinary Links:")[1]
                .split("Additional Comments:")[0]
                .strip()
            )
            additional_comments = user_query.split("Additional Comments:")[1].strip()

            # Create instance of IEPEditInput
            unit_plan_data = GenerateUnitPlan(
                grade=grade,
                unit_title=unit_title,
                subject=subject,
                unit_objectives=unit_objectives,
                standard=standard,
                length_of_a_unit=length_of_a_unit,
                assessment_strategies=assessment_strategies,
                interdisciplinary_links=interdisciplinary_links,
                additional_comments=additional_comments,
            )
            return unit_plan_data

        except Exception as e:
            print(f"An error occurred while fetching Unit plan input data: {str(e)}")
            return None

    def fetch_feedback_response_data(self, user_id: str) -> GenerateFeedback:
        try:
            # Fetch the latest diffrentiation_id
            latest_feedback_response = (
                self.db.table("uc_feedback_generator")
                .select("feedback_id, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            feedback_id = latest_feedback_response.data[0]["feedback_id"]
            response = (
                self.db.table("uc_feedback_generator")
                .select("user_query")
                .eq("feedback_id", feedback_id)
                .execute()
            )
            user_query = response.data[0]["user_query"]

            # Extract data from user_query
            assignment = (
                user_query.split("Assignment/Project:")[1]
                .split("Feedback Criteria:")[0]
                .strip()
            )
            feedback_criteria = (
                user_query.split("Feedback Criteria:")[1]
                .split("Achievement Levels:")[0]
                .strip()
            )
            achievement_levels = (
                user_query.split("Achievement Levels:")[1]
                .split("Standards Alignment:")[0]
                .strip()
            )
            standards_alignment = (
                user_query.split("Standards Alignment:")[1]
                .split("Tone and Style Controls:")[0]
                .strip()
            )
            tone_and_style_controls = user_query.split("Tone and Style Controls:")[
                1
            ].strip()

            # Create instance of IEPEditInput
            feedback_plan_data = GenerateFeedback(
                assignment=assignment,
                feedback_criteria=feedback_criteria,
                achievement_levels=achievement_levels,
                standards_alignment=standards_alignment,
                tone_and_style_controls=tone_and_style_controls,
            )
            return feedback_plan_data

        except Exception as e:
            print(
                f"An error occurred while fetching feedback plan input data: {str(e)}"
            )
            return None

    # Fetches all history ids for clear all
    def fetch_all_history_ids(self, user_id: str) -> Optional[List[str]]:
        try:
            response = (
                self.db.table("uc_chat_history")
                .select("chat_history_id")
                .eq("user_id", user_id)
                .execute()
            )
            history_ids = [item["chat_history_id"] for item in response.data]
            return history_ids
        except Exception as e:
            print(f"An error occurred while fetching history IDs: {str(e)}")
            return None

    def fetch_all_ids(self, user_id: str, agent_details: dict) -> Optional[List[str]]:
        try:
            table_one = agent_details["table_name_one"]
            id_column = agent_details["id_column_one"]

            response = (
                self.db.table(table_one)
                .select(id_column)
                .eq("user_id", user_id)
                .execute()
            )
            history_ids = [item[id_column] for item in response.data]
            return history_ids
        except Exception as e:
            print(f"An error occurred while fetching history IDs: {str(e)}")
            return None

    # Deletes all the history ids for a particular user
    def delete_all_history_for_user(self, user_id: str):
        try:
            # Fetch all chat history IDs for the given user_id
            history_ids = self.fetch_all_history_ids(user_id)

            if not history_ids:
                print("No chat history found for the user.")
                return {"message": "No chat history found for the user."}

            # Delete each chat history record
            for history_id in history_ids:
                self.delete_history_intreactive_chat(history_id)

            return {"message": "All chat history deleted successfully!"}
        except Exception as e:
            print(f"An error occurred while deleting history: {str(e)}")
            return {"message": f"Failed to delete chat history: {str(e)}"}

    def delete_all_history(self, user_id: str, agent_details: dict):
        try:
            # Fetch all chat history IDs for the given user_id
            history_ids = self.fetch_all_ids(user_id, agent_details)

            if not history_ids:
                print("No chat history found for the user.")
                return {"message": "No chat history found for the user."}

            # Delete each chat history record
            for history_id in history_ids:
                self.delete_history_chat(history_id, agent_details)

            return {"message": "All chat history deleted successfully!"}
        except Exception as e:
            print(f"An error occurred while deleting history: {str(e)}")
            return {"message": f"Failed to delete chat history: {str(e)}"}

    # This will favorite or unfavorite a particular chat id
    def mark_favorite(self, id: str, favorite: bool, agent_type: str):
        from config.agent_details import AGENT_DETAILS

        try:
            agent_details = AGENT_DETAILS[agent_type]
            table_name = agent_details["table_name_one"]
            id_column = agent_details["id_column_one"]
            favorite_column = agent_details["favorite"]

            # Try to mark the chat_msg_id as favorite
            response = (
                self.db.table(table_name)
                .update({favorite_column: favorite})
                .eq(id_column, id)
                .execute()
            )

            # This is mainly for chat_msg_id, if there is a valid response, then we mark it as favorite
            if response and response.data:
                if favorite:
                    print(f"Marked {id_column} {id} as favorite!")
                else:
                    print(f"Unmarked {id_column} {id} as favorite!")

                # If the identifier is chat_msg_id, also favorite the history_id
                if table_name == "uc_chat_msg" and id_column == "chat_msg_id":
                    history_response = (
                        self.db.table(table_name)
                        .select("history_id")
                        .eq(id_column, id)
                        .execute()
                    )

                    if history_response.data:
                        history_id = history_response.data[0]["history_id"]

                        # Mark the history_id as favorite
                        self.mark_favorite(history_id, favorite, "ai_coach_history")

                return True

            # Otherwise if it fails to find a chat_msg_id, it will try to look for a history id in ai_coach_history
            else:
                print(
                    f"Failed to update favorite status for {id_column} {id}. Attempting to mark as history_id."
                )

                # Try to mark the history_id as favorite
                agent_details = AGENT_DETAILS["ai_coach_history"]
                table_name = agent_details["table_name_one"]
                id_column = agent_details["id_column_one"]

                response = (
                    self.db.table(table_name)
                    .update({favorite_column: favorite})
                    .eq(id_column, id)
                    .execute()
                )

                if response and response.data:
                    if favorite:
                        print(f"Marked {id_column} {id} as favorite!")
                    else:
                        print(f"Unmarked {id_column} {id} as favorite!")

                    return True
                else:
                    print(f"Failed to update favorite status for {id_column} {id}.")
                    return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    # This will fetch all the chats of a particular user which have favorite as TRUE
    def fetch_favorite_chats(
        self, user_id: str, favorite: bool, agent_type: str
    ) -> Optional[List[FavoriteRequest]]:
        from config.agent_details import AGENT_DETAILS

        try:
            agent_details = AGENT_DETAILS[agent_type]
            table_name = agent_details["table_name_one"]
            id_column = agent_details["id_column_one"]
            favorite_column = agent_details["favorite"]

            response = (
                self.db.table(table_name)
                .select(
                    f"{id_column}, user_id, {favorite_column}, summary_title, edited_title"
                )
                .eq("user_id", user_id)
                .eq(favorite_column, favorite)
                .order("created_at")
                .execute()
            )

            # If there are no favorite chats
            if not response.data:
                print("There are no favorite chats.")
                return []

            favorite_chats = [
                FavoriteRequest(
                    message_id=item[id_column],
                    user_id=item["user_id"],
                    user_query=item["edited_title"]
                    if item["edited_title"]
                    else item["summary_title"],
                    is_favorite=item[favorite_column],
                )
                for item in response.data
            ]
            return favorite_chats
        except Exception as e:
            print(f"An error occurred while fetching favorite chats: {str(e)}")
            return None

    # Helper function to retrieve any chat ID based on a few parameters from the database
    def fetch_by_id(
        self,
        first_table_name: str,
        second_table_name: str,
        third_tabel_name: str,
        record_id: str,
        id_column_one: str,
        id_column_two: str,
        response_field_one: str,
        response_field_two: str,
        response_field_three: str,
        session_id: str,
        refrence_id_one: str,
        refrence_id_two: str,
        model: Type[BaseModel],
    ) -> Optional[BaseModel]:
        try:
            response_first_table_name = (
                self.db.table(first_table_name)
                .select("*")
                .eq(id_column_one, record_id)
                .order("created_at")
                .execute()
            )
            # print("response_first_table_name - ", response_first_table_name)
            response_second_table_name = (
                self.db.table(second_table_name)
                .select("*")
                .eq(id_column_two, record_id)
                .order("created_at")
                .execute()
            )
            response_third_table_name = (
                self.db.table(third_tabel_name)
                .select("*")
                .eq("action_id", record_id)
                .order("created_at")
                .execute()
            )
            # print("response_second_table_name - ", response_second_table_name)
            if response_first_table_name.data != []:
                final_response = model(
                    response=response_first_table_name.data[0][response_field_one],
                    table_name=first_table_name,
                )
                foregin_id = "Not required"
                foregin_table_name = first_table_name

            elif response_second_table_name.data != []:
                final_response = model(
                    response=response_second_table_name.data[0][response_field_two],
                    table_name=second_table_name,
                )
                foregin_id = response_second_table_name.data[0][session_id]
                foregin_table_name = second_table_name
            else:
                final_response = model(
                    response=response_third_table_name.data[0][response_field_three],
                    table_name=third_tabel_name,
                )
                foregin_id = response_third_table_name.data[0][refrence_id_one]
                foregin_table_name = first_table_name
                if not foregin_id:
                    foregin_id = response_third_table_name.data[0][refrence_id_two]
                    foregin_table_name = second_table_name

            return [final_response, foregin_id, foregin_table_name]
        except Exception as e:
            print(f"Exception occurred while fetching data from table: {str(e)}")
            return None

    def fetch_by_id_for_aicoach(
        self,
        first_table_name: str,
        second_table_name: str,
        record_id: str,
        id_column_one: str,
        id_column_two: str,
        response_field_one: str,
        response_field_two: str,
        session_id: str,
        refrence_id: str,
        model: Type[BaseModel],
    ) -> Optional[BaseModel]:
        try:
            response_first_table_name = (
                self.db.table(first_table_name)
                .select("*")
                .eq(id_column_one, record_id)
                .order("created_at")
                .execute()
            )
            # print("response_first_table_name - ", response_first_table_name)
            response_second_table_name = (
                self.db.table(second_table_name)
                .select("*")
                .eq(id_column_two, record_id)
                .order("created_at")
                .execute()
            )
            # print("response_second_table_name - ", response_second_table_name)
            if response_first_table_name.data != []:
                final_response = model(
                    response=response_first_table_name.data[0][response_field_one],
                    table_name=first_table_name,
                )
                reference_id = response_first_table_name.data[0][session_id]
            else:
                final_response = model(
                    response=response_second_table_name.data[0][response_field_two],
                    table_name=second_table_name,
                )
                reference_id = response_second_table_name.data[0][refrence_id]

            return (final_response, reference_id)
        except Exception as e:
            print(f"Exception occurred while fetching data from table: {str(e)}")
            return None

    # Function to update the AI response in the database
    def update_entry(
        self, table_name: str, id_column: str, entry_id: str, update_data: dict
    ) -> bool:
        try:
            response = (
                self.db.table(table_name)
                .update(update_data)
                .eq(id_column, entry_id)
                .execute()
            )

            # Checking for responses
            if hasattr(response, "status") and response.status == 200:
                return True
            elif hasattr(response, "data") and response.data:
                return True
            else:
                print(f"Update failed with response data: {response}")
                return False
        except Exception as e:
            print(f"An error occurred while updating the entry: {str(e)}")
            return False

    # Function to update the AI response in the database
    def update_response_in_database(
        self,
        table_name: str,
        column_name: str,
        record_id: str,
        translated_text: str,
        id_column: str,
    ) -> bool:
        try:
            response = (
                self.db.table(table_name)
                .update({column_name: translated_text})
                .eq(id_column, record_id)
                .execute()
            )

            if response.data:
                return True
            return False
        except Exception as e:
            print(
                f"Exception occurred while updating {column_name} in {table_name}: {str(e)}"
            )
            return False


def get_storage() -> SupabaseStorage:
    if not hasattr(get_storage, "instance"):
        get_storage.instance = SupabaseStorage()
    return get_storage.instance
