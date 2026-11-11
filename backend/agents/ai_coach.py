import asyncio
import json
import time
import uuid
from typing import Optional
from config.azure_provider import acompletion
from prompts.bot_prompts import fiona_prompt, interactivechat_title_prompt
from dotenv import load_dotenv
from db.remote_storage import SupabaseStorage
from config.action_items_agents import ActionAgents

load_dotenv()


class AICoach(ActionAgents):
    def __init__(self, apiKey: str, model: str) -> None:
        self.chat_messages = [{"role": "system", "content": fiona_prompt}]
        self.selected_coach = "fiona"
        self.response_queue = asyncio.Queue()
        self.response_chunks = []
        self.storage = SupabaseStorage()  # Initialize Supabase storage
        self.model = model
        self.apiKey = apiKey
        self.query_track = 0
        # self.abort_event = asyncio.Event()  # Event to signal abortion

    def generate_chat_id(self) -> str:
        return str(uuid.uuid4())

    def reset_abort_event(self):
        self.abort_event.clear()

    def get_complete_response(self) -> str:
        return "".join([chunk for chunk in self.response_chunks])

    async def chat(
        self,
        query: str,
        history_id: str,
        user_id: str,
        chat_id: Optional[str] = None,
    ):
        chat_msg_track = 0
        if chat_id is None:
            chat_id = self.generate_chat_id()
            print(f"generating chat with id {chat_id}")
            chat_msg_track += 1

        await self.response_queue.put(json.dumps({"id": chat_id}))

        self.chat_messages.append({"role": "user", "content": query})
        try:
            agent_response = await acompletion(
                model=self.model,
                api_key=self.apiKey,
                messages=self.chat_messages,
                stream=True,
            )
        except Exception as e:
            raise Exception(f"Error during AI Response: {e}")

        # self.reset_abort_event()  # Reset the abort signal

        async for chunk in agent_response:
            # if self.abort_event.is_set():  # Check if abort signal is raised
            #     print("Aborting response generation")
            #     return
            msg = chunk.choices[0].delta.content or ""
            self.response_chunks.append(msg)
            await self.response_queue.put(msg)
        self.chat_messages.append(
            {"role": "assistant", "content": self.get_complete_response()}
        )
        if self.query_track == 0:
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
            self.query_track += 1
            # Store the user_id and history_id in the uc_chat_history table
            self.storage.add_chat_history(
                history_id=history_id,
                user_id=user_id,
                summary_title=title_to_save,
            )

        complete_response = self.get_complete_response()

        if chat_msg_track == 0:
            self.storage.store_edited_response(
                chat_id=chat_id,
                user_msg=query,
                coach_response=complete_response,
            )
        else:
            self.storage.add_interactive_chat(
                chat_msg_id=chat_id,
                user_query=query,
                coach_response=complete_response,
                history_id=history_id,
            )
        self.response_chunks.clear()

        # # Generate suggested prompts and append to the generation response
        # suggested_prompts = await self.generate_suggested_prompts(complete_response)
        # await self.response_queue.put(
        #     json.dumps(
        #         {
        #             "suggested_prompts": suggested_prompts,
        #         }
        #     )
        # )

    async def chat_with_document(self, query: str, query_engine):
        self.chat_messages.append({"role": "user", "content": query})
        agent_response = query_engine.query(query)

        for chunk in agent_response.response_gen:
            msg = chunk or ""
            self.response_chunks.append(msg)
            await self.response_queue.put(msg)
        self.chat_messages.append(
            {"role": "assistant", "content": self.get_complete_response()}
        )
        self.response_chunks.clear()

    # Function to generate some suggested prompts based on the first diffrentiation plan made
    async def generate_suggested_prompts(self, first_output: str) -> list:
        prompt_message = [
            {
                "role": "system",
                "content": 'Based on this output, provide some questions or recommended actions that a teacher can ask to better implement this in a classroom. Please make your suggestions from teacher\'s perspective such as \\"Create X for me\\" or \\"Give me an example of X\\". You have to generate 5 such questions/suggestions and all of these should be less than 10-15 words.\nAlso rank them on relevance with most relevant on top in context to the output generated. Please separate each prompt with a newline and don\'t list them with bullet points or numbers.',
            },
            {"role": "user", "content": first_output},
        ]
        try:
            agent_response = await acompletion(
                model=self.model,
                api_key=self.apiKey,
                messages=prompt_message,
                max_tokens=1000,
            )
            prompts = agent_response["choices"][0]["message"]["content"].split("\n")
            return [prompt for prompt in prompts if prompt]
        except Exception as e:
            raise Exception(f"Error generating suggested prompts: {e}")

    # Added another function so that the AI coach can translate text to a particular response.
    async def translate(
        self,
        text: str,
        table_name: str,
        chat_msg_id: str,
        target_language: str,
        remote_storage: SupabaseStorage,
    ):
        print("generating translation....")
        st = time.time()
        translation_id = self.generate_chat_id()
        # Check and regenerate translation_id if it matches assessment_id
        while translation_id == chat_msg_id:
            print(
                f"regenerating translation_id as it matches chat_msg_id {chat_msg_id}"
            )
            translation_id = self.generate_chat_id()

        print(f"generating translation with id {translation_id}")
        yield json.dumps({"id": translation_id})
        translation_prompt = f"Translate the entire following text to {target_language}, keeping the context intact:\n\n{text}"
        action_query = f"Translate it to {target_language}"
        try:
            agent_response = await acompletion(
                model=self.model,
                api_key=self.apiKey,
                messages=[{"role": "user", "content": translation_prompt}],
                max_tokens=4000,
                stream=True,
            )
        except Exception as e:
            raise Exception(f"Error during translation: {e}")
        et = time.time()
        print(f"starting streaming in {et-st} seconds")
        async for chunk in agent_response:
            translated_text = chunk.choices[0].delta.content or ""
            self.response_chunks.append(translated_text)
            yield json.dumps(
                {
                    "chunk": translated_text,
                }
            )

        translated_text = self.get_complete_response()
        try:
            # Storing assesment response to database
            remote_storage.add_chat_quick_action(
                action_id=translation_id,
                action_query=action_query,
                action_response=translated_text,
                original_id=chat_msg_id,
                action_type="Translate",
                table_name=table_name,
            )

        except Exception as e:
            raise Exception(f"Error storing assessment: {e}")
