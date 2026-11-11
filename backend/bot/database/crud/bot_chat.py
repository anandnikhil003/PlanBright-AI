import asyncio
import json
import uuid
from config.azure_provider import acompletion
from .bot import BotCRUD
from .bots_chat_record_fun import Bot_Chat_Record
from prompts.bot_prompts import interactivechat_title_prompt
from .bot_file import BotFileCRUD
from config.azure_provider import azure_openai_client, azure_embedding_deployment
import dotenv
import os
from typing import Optional


dotenv.load_dotenv()


class Bot_chat_agent:
    def __init__(self, apikey: str, model: str):
        self.response_queue = asyncio.Queue()
        self.response_chunk = []
        self.bot_data = BotCRUD()
        self.bot_instruction = []
        self.query_count = 0
        self.session_bot_id = ""
        self.bot_chat_data = Bot_Chat_Record()
        self.bot_file_data = BotFileCRUD()
        self.model = model
        self.apiKey = apikey

    def generate_bot_chat_id(self) -> str:
        return str(uuid.uuid4())

    def get_complete_response(self) -> str:
        return "".join([chunk for chunk in self.response_chunk])

    async def bot_chat(
        self,
        bot_id: str,
        query: str,
        user_id: Optional[str] = None,
        bot_type: Optional[str] = None,
        iframe_id: Optional[str] = None,
        finger_print_id: Optional[str] = None,
        reset: Optional[bool] = None,
    ):
        bot_chat_id = self.generate_bot_chat_id()
        print(f"generating bot chat with id {bot_chat_id}")

        await self.response_queue.put(json.dumps({"id": bot_chat_id}))

        if self.query_count == 0:
            print("self.query_count", self.query_count)
            if bot_type == "temporary":
                self.bot_instruction.append(
                    {
                        "role": "system",
                        "content": self.bot_data.get_updated_system_instruction(
                            bot_id=bot_id
                        ),
                    }
                )
            else:
                self.bot_instruction.append(
                    {
                        "role": "system",
                        "content": self.bot_data.get_system_instruction(bot_id=bot_id),
                    }
                )

            response = self.bot_file_data.bot_embedding_information(bot_id=bot_id)
            print("response ----------", response, "--------------")
            if response:
                client = azure_openai_client()
                try:
                    embedding_created = client.embeddings.create(
                        input=query,
                        model=azure_embedding_deployment(),
                        encoding_format="float",
                    )
                    # Extract the embedding vector
                    query_embeddings = embedding_created.data[0].embedding
                    print("query_embedding ------", query_embeddings, "----------")
                except Exception as e:
                    print(f"Error generating query embeddings: {e}")

                similar_embedding_info = self.bot_file_data.search_relevant_embedding(
                    query_embedding=query_embeddings, bot_id=bot_id
                )
                print(
                    "similar_embedding_info --------------",
                    similar_embedding_info,
                    "---------------",
                )
                if similar_embedding_info:
                    for element in similar_embedding_info:
                        document_instructions = element["text_content"]
                        self.bot_instruction.append(
                            {"role": "system", "content": document_instructions}
                        )
            self.query_count += 1

        self.bot_instruction.append({"role": "user", "content": query})
        try:
            agent_response = await acompletion(
                model=self.model,
                api_key=self.apiKey,
                messages=self.bot_instruction,
                stream=True,
            )
        except Exception as e:
            raise Exception(f"Error during AI Response: {e}")
        async for chunk in agent_response:
            msg = chunk.choices[0].delta.content or ""
            self.response_chunk.append(msg)
            await self.response_queue.put(msg)

        self.bot_instruction.append(
            {"role": "assistant", "content": self.get_complete_response()}
        )
        print("-------------", self.bot_instruction, "-------------")
        if user_id and not iframe_id and not finger_print_id:
            if bot_type != "temporary":
                print("self.query_count 2", self.query_count)
                if self.query_count == 1:
                    print(self.query_count)
                    self.session_bot_id = self.generate_bot_chat_id()
                    title_generation_message = [
                        {"role": "system", "content": interactivechat_title_prompt},
                        {"role": "user", "content": self.get_complete_response()},
                    ]
                    try:
                        agent_response = await acompletion(
                            model=self.model,
                            api_key=self.apiKey,
                            messages=title_generation_message,
                            max_tokens=3000,
                        )
                    except Exception as e:
                        raise Exception(f"Error during AI Response: {e}")
                    title_to_save = agent_response["choices"][0]["message"]["content"]
                    if title_to_save.startswith('"') and title_to_save.endswith('"'):
                        title_to_save = title_to_save[1:-1]
                    self.query_count += 1
                    # Store the user_id and history_id in the uc_chat_history table
                    self.bot_chat_data.add_bot_engagment(
                        id=self.session_bot_id,
                        bot_id=bot_id,
                        user_id=user_id,
                        messages_sent=title_to_save,
                        iframe_id=iframe_id,
                        finger_print_id=finger_print_id,
                    )

                complete_bot_response = self.get_complete_response()
                try:
                    self.bot_chat_data.add_chat_record(
                        chat_id=bot_chat_id,
                        chat_message=query,
                        bot_response=complete_bot_response,
                        bot_session_id=self.session_bot_id,
                    )

                except Exception as e:
                    print(
                        f"There is an error storing the chat record of bot in a session: {e}"
                    )
        # Case 2: Only `iframe_id` and `finger_print_id` exist
        elif not user_id and iframe_id and finger_print_id:
            if self.query_count == 1:
                # Check if session_id exists for iframe_id and finger_print_id
                session_id = self.bot_data.get_session_id_for_iframe(
                    iframe_id, finger_print_id
                )
                if session_id is None:
                    # Create a new session_id
                    self.session_bot_id = self.generate_bot_chat_id()
                    title_generation_message = [
                        {"role": "system", "content": interactivechat_title_prompt},
                        {"role": "user", "content": self.get_complete_response()},
                    ]
                    try:
                        agent_response = await acompletion(
                            model=self.model,
                            api_key=self.apiKey,
                            messages=title_generation_message,
                            max_tokens=3000,
                        )
                    except Exception as e:
                        raise Exception(f"Error during AI Response: {e}")
                    title_to_save = agent_response["choices"][0]["message"]["content"]
                    if title_to_save.startswith('"') and title_to_save.endswith('"'):
                        title_to_save = title_to_save[1:-1]
                    self.query_count += 1
                    # Store the user_id and history_id in the uc_chat_history table
                    self.bot_chat_data.add_bot_engagment(
                        id=self.session_bot_id,
                        bot_id=bot_id,
                        user_id=user_id,
                        messages_sent=title_to_save,
                        iframe_id=iframe_id,
                        finger_print_id=finger_print_id,
                    )
                elif reset:
                    if self.query_count == 1:
                        self.session_bot_id = self.generate_bot_chat_id()

                        title_generation_message = [
                            {"role": "system", "content": interactivechat_title_prompt},
                            {"role": "user", "content": self.get_complete_response()},
                        ]
                        try:
                            agent_response = await acompletion(
                                model=self.model,
                                api_key=self.apiKey,
                                messages=title_generation_message,
                                max_tokens=3000,
                            )
                        except Exception as e:
                            raise Exception(f"Error during AI Response: {e}")
                        title_to_save = agent_response["choices"][0]["message"][
                            "content"
                        ]
                        if title_to_save.startswith('"') and title_to_save.endswith(
                            '"'
                        ):
                            title_to_save = title_to_save[1:-1]
                        self.query_count += 1
                        # Store the user_id and history_id in the uc_chat_history table
                        self.bot_chat_data.add_bot_engagment(
                            id=self.session_bot_id,
                            bot_id=bot_id,
                            user_id=user_id,
                            messages_sent=title_to_save,
                            iframe_id=iframe_id,
                            finger_print_id=finger_print_id,
                        )
                else:
                    self.session_bot_id = session_id
                    self.query_count += 1
            complete_bot_response = self.get_complete_response()
            try:
                self.bot_chat_data.add_chat_record(
                    chat_id=bot_chat_id,
                    chat_message=query,
                    bot_response=complete_bot_response,
                    bot_session_id=self.session_bot_id,
                )

            except Exception as e:
                print(
                    f"There is an error storing the chat record of bot in a session: {e}"
                )
        # Case 3: All three parameters exist
        elif user_id and iframe_id and finger_print_id:
            if self.query_count == 1:
                session_id = self.bot_data.get_session_id_for_logged_in_iframe(
                    iframe_id, user_id
                )
                if session_id is None:
                    # Create a new session_id
                    self.session_bot_id = self.generate_bot_chat_id()
                    title_generation_message = [
                        {"role": "system", "content": interactivechat_title_prompt},
                        {"role": "user", "content": self.get_complete_response()},
                    ]
                    try:
                        agent_response = await acompletion(
                            model=self.model,
                            api_key=self.apiKey,
                            messages=title_generation_message,
                            max_tokens=3000,
                        )
                    except Exception as e:
                        raise Exception(f"Error during AI Response: {e}")
                    title_to_save = agent_response["choices"][0]["message"]["content"]
                    if title_to_save.startswith('"') and title_to_save.endswith('"'):
                        title_to_save = title_to_save[1:-1]
                    self.query_count += 1
                    # Store the user_id and history_id in the uc_chat_history table
                    self.bot_chat_data.add_bot_engagment(
                        id=self.session_bot_id,
                        bot_id=bot_id,
                        user_id=user_id,
                        messages_sent=title_to_save,
                        iframe_id=iframe_id,
                        finger_print_id=finger_print_id,
                    )
                elif reset:
                    if self.query_count == 1:
                        self.session_bot_id = self.generate_bot_chat_id()
                        print(f"New session ID generated: {self.session_bot_id}")
                        title_generation_message = [
                            {"role": "system", "content": interactivechat_title_prompt},
                            {"role": "user", "content": self.get_complete_response()},
                        ]
                        try:
                            agent_response = await acompletion(
                                model=self.model,
                                api_key=self.apiKey,
                                messages=title_generation_message,
                                max_tokens=3000,
                            )
                        except Exception as e:
                            raise Exception(f"Error during AI Response: {e}")
                        title_to_save = agent_response["choices"][0]["message"][
                            "content"
                        ]
                        if title_to_save.startswith('"') and title_to_save.endswith(
                            '"'
                        ):
                            title_to_save = title_to_save[1:-1]
                        self.query_count += 1
                        # Store the user_id and history_id in the uc_chat_history table
                        self.bot_chat_data.add_bot_engagment(
                            id=self.session_bot_id,
                            bot_id=bot_id,
                            user_id=user_id,
                            messages_sent=title_to_save,
                            iframe_id=iframe_id,
                            finger_print_id=finger_print_id,
                        )
                else:
                    update_result = self.bot_data.update_fingerprint(
                        session_id, iframe_id, user_id, finger_print_id
                    )
                    print(update_result)
                    self.session_bot_id = session_id
                    self.query_count += 1
            complete_bot_response = self.get_complete_response()
            try:
                self.bot_chat_data.add_chat_record(
                    chat_id=bot_chat_id,
                    chat_message=query,
                    bot_response=complete_bot_response,
                    bot_session_id=self.session_bot_id,
                )

            except Exception as e:
                print(
                    f"There is an error storing the chat record of bot in a session: {e}"
                )

        self.response_chunk.clear()
