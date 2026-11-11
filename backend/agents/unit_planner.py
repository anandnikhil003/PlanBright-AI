import os
import time
import asyncio
import uuid
import json
from dotenv import load_dotenv
from config.azure_provider import acompletion
from db.remote_storage import SupabaseStorage
from prompts.bot_prompts import unit_planner_prompt, unit_planner_title_prompt
from db.interaction_manager import InteractionManager
from config.action_items_agents import ActionAgents
from typing import Optional, Dict, Any
from prompts.bot_prompts import extended_chat_prompt

load_dotenv()


class UnitPlanner(ActionAgents):
    def __init__(self, apiKey: str, model: str) -> None:
        self.model = model
        self.apiKey = apiKey
        self.response_chunks = []

    def generate_unitplan_id(self) -> str:
        return str(uuid.uuid4())

    async def generate_unitplan(
        self,
        query: str,
        remote_storage: SupabaseStorage,
        user_id: str,
        interaction_manager: InteractionManager,
    ):
        print("generating Unit Plan....")
        unitplan_generator_id = self.generate_unitplan_id()
        print(f"generating unit plan with id {unitplan_generator_id}")
        yield json.dumps({"id": unitplan_generator_id})
        await asyncio.sleep(0.02)  # wait for 20ms
        messages = [
            {"role": "system", "content": unit_planner_prompt},
            {"role": "user", "content": query},
        ]
        st = time.time()
        try:
            agent_response = await acompletion(
                model=self.model, api_key=self.apiKey, messages=messages, stream=True
            )
        except Exception as e:
            raise Exception(f"Error during AI Response: {e}")
        et = time.time()
        print(f"starting streaming in {et-st} seconds")

        async for chunk in agent_response:
            unitplan_chunk = chunk.choices[0].delta.content or ""
            self.response_chunks.append(unitplan_chunk)
            yield json.dumps({"chunk": unitplan_chunk})

        complete_response = self.get_complete_unit_response()
        # print(complete_response)
        title_generation_message = [
            {"role": "system", "content": unit_planner_title_prompt},
            {"role": "user", "content": query},
        ]

        try:
            agent_response_title = await acompletion(
                model=self.model,
                api_key=self.apiKey,
                messages=title_generation_message,
                max_tokens=3000,
            )
        except Exception as e:
            raise Exception(f"Error during AI Response: {e}")

        title_to_save = agent_response_title["choices"][0]["message"]["content"]
        title_to_save = title_to_save.strip('"')
        try:
            # Add the interaction count
            interaction_manager.add_interaction_Unit(user_id)

            # Storing assessment response to the database
            remote_storage.add_unitplan(
                unitplan_id=unitplan_generator_id,
                user_query=query,
                unitplan_response=complete_response,
                user_id=user_id,
                summary_title=title_to_save,
            )

            # # Generate suggested prompts and append to the generation response
            # suggested_prompts = await self.generate_suggested_prompts(complete_response)
            # yield json.dumps(
            #     {
            #         "suggested_prompts": suggested_prompts,
            #     }
            # )
        except Exception as e:
            raise Exception(f"Error storing Unit Plan: {e}")

    def get_complete_unit_response(self) -> str:
        return "".join([chunk for chunk in self.response_chunks])

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

    # Added another function so that the Unit Planner can translate text to a particular response.
    async def translate(
        self,
        text: str,
        table_name: str,
        unitplan_id: str,
        target_language: str,
        remote_storage: SupabaseStorage,
    ):
        print("generating translation....")
        st = time.time()
        translation_id = self.generate_unitplan_id()
        # Check and regenerate translation_id if it matches unitplan_id
        while translation_id == unitplan_id:
            print(
                f"regenerating translation_id as it matches unitplan_id {unitplan_id}"
            )
            translation_id = self.generate_unitplan_id()

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

        translated_text = self.get_complete_unit_response()
        try:
            # Storing lesson plan response to database
            remote_storage.add_unitplan_quick_action(
                action_id=translation_id,
                action_query=action_query,
                action_response=translated_text,
                original_id=unitplan_id,
                action_type="Translate",
                table_name=table_name,
            )

        except Exception as e:
            raise Exception(f"Error storing unitplan quickaction: {e}")


class Unitchat:
    def __init__(self) -> None:
        self.storage = SupabaseStorage()  # Initialize Supabase storage
        self.chat_messages = [{"role": "system", "content": extended_chat_prompt}]
        self.response_queue = asyncio.Queue()
        self.response_chunks = []

    def generate_unitplan_chat_id(self) -> str:
        return str(uuid.uuid4())

    def get_complete_response(self) -> str:
        return "".join([chunk for chunk in self.response_chunks])

    async def chat(
        self,
        query: str,
        unitplan_history_id: str,
        agent_details: Dict[str, Any],
        chat_id: Optional[str] = None,
    ):
        chat_msg_track = 0
        if chat_id is None:
            chat_id = self.generate_unitplan_chat_id()
            print(f"generating chat with id {chat_id}")
            chat_msg_track += 1

        await self.response_queue.put(json.dumps({"id": chat_id}))

        # Fetch the context list
        context = self.storage.get_context_list(unitplan_history_id, agent_details)

        # Optimization: Create a set of unique identifiers from `self.chat_messages`
        # This set will store tuples of (role, content) for O(1) lookup.
        existing_messages_set = {
            (msg["role"], msg["content"]) for msg in self.chat_messages
        }
        # Append missing context items efficiently
        for i, context_item in enumerate(context):
            if i == 0:
                # Create a tuple identifier from the context item
                context_identifier = (context_item["role"], context_item["content"])
                # Check if the context item is already in the chat messages set
                if context_identifier not in existing_messages_set:
                    self.chat_messages.append(context_item)  # Add it if missing
                    # Add the new context item to the set to keep it up to date
                    existing_messages_set.add(context_identifier)
            else:
                context_user, context_assistance = context_item
                # Create a tuple identifier from the context item
                context_identifier = (
                    context_assistance["role"],
                    context_assistance["content"],
                )
                # Check if the context item is already in the chat messages set
                if context_identifier not in existing_messages_set:
                    self.chat_messages.append(context_user)
                    self.chat_messages.append(context_assistance)  # Add it if missing
                    # Add the new context item to the set to keep it up to date
                    existing_messages_set.add(context_identifier)

        self.chat_messages.append({"role": "user", "content": query})
        try:
            agent_response = await acompletion(
                model=os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o"),
                api_key=os.getenv("AZURE_API_KEY"),
                messages=self.chat_messages,
                stream=True,
            )
        except Exception as e:
            raise Exception(f"Error during AI Response: {e}")

        async for chunk in agent_response:
            msg = chunk.choices[0].delta.content or ""
            self.response_chunks.append(msg)
            await self.response_queue.put(msg)

        self.chat_messages.append(
            {"role": "assistant", "content": self.get_complete_response()}
        )

        complete_response = self.get_complete_response()

        if chat_msg_track == 0:
            self.storage.store_edited_response_unitplan_chat(
                chat_id=chat_id,
                user_msg=query,
                chat_response=complete_response,
            )
        else:
            self.storage.add_unitplan_chat(
                chat_msg_id=chat_id,
                user_query=query,
                chat_response=complete_response,
                unitplan_history_id=unitplan_history_id,
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
                model=os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o"),
                api_key=os.getenv("AZURE_API_KEY"),
                messages=prompt_message,
                max_tokens=1000,
            )
            prompts = agent_response["choices"][0]["message"]["content"].split("\n")
            return [prompt for prompt in prompts if prompt]
        except Exception as e:
            raise Exception(f"Error generating suggested prompts: {e}")


def get_unit_planner_generator() -> UnitPlanner:
    return UnitPlanner(apiKey=os.getenv("AZURE_API_KEY"), model=os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o"))
