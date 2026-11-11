import os
import time
import asyncio
import uuid
import json
import pandas as pd
from dotenv import load_dotenv
from config.azure_provider import acompletion
from db.remote_storage import SupabaseStorage
from prompts.bot_prompts import assessment_prompt, assessment_title_prompt
from db.interaction_manager import InteractionManager
from config.action_items_agents import ActionAgents
from typing import Optional, Dict, Any
from prompts.bot_prompts import extended_chat_prompt

load_dotenv()


def get_assesment_examples() -> str:
    examples = """"""
    example_template = """
        Example {index}
        Subject: {query}
        Grade: {grade}
        Topic: {topic}
        Standards: {standard}
        Preferred Assesment Types: {assesment_type}
        Assesment: 
        {assesment}
        --------------------------------------------
    """
    file_name = os.path.join("data", "assesment_generator", "assesment_examples.csv")
    df = pd.read_csv(file_name)
    print(df)
    for index, row in df.iterrows():
        example = example_template.format(
            index=index + 1,
            query=row["Subject"],
            grade=row["Grade"],
            topic=row["Topic"],
            standard=row["Standards"],
            assesment_type=row["Preferred Assessment Type"],
            assesment=row["Response"],
        )
        examples += example
    return examples


assesment_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_assesment_examples",
            "description": "Get relevant assesment examples",
        },
    }
]

available_functions = {
    "get_assesment_examples": get_assesment_examples,
}


class AssesmentGenerator(ActionAgents):
    def __init__(self, apiKey: str, model: str) -> None:
        self.model = model
        self.apiKey = apiKey
        self.response_chunks = []

    def generate_assesment_id(self) -> str:
        return str(uuid.uuid4())

    async def generate_assesment(
        self,
        query: str,
        remote_storage: SupabaseStorage,
        user_id: str,
        interaction_manager: InteractionManager,
    ):
        print("generating assesment....")
        assesment_id = self.generate_assesment_id()
        print(f"generating assesment with id {assesment_id}")
        yield json.dumps({"id": assesment_id})
        await asyncio.sleep(0.02)  # wait for 20ms
        messages = [
            {"role": "system", "content": assessment_prompt},
            {"role": "user", "content": query},
        ]
        st = time.time()
        try:
            agent_response = await acompletion(
                model=self.model,
                api_key=self.apiKey,
                messages=messages,
                tools=assesment_tools,
            )
        except Exception as e:
            raise Exception(f"Error during AI Response: {e}")
        response_message = agent_response.choices[0].message
        messages.append(response_message)
        tool_calls = response_message.tool_calls
        if tool_calls:
            # call the tools over here and add those in the response msg
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                if function_to_call:
                    try:
                        print(f"calling {function_name}")
                        function_response = function_to_call()
                    except Exception as e:
                        raise Exception(f"Error calling function {function_name}: {e}")
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )
        try:
            agent_response = await acompletion(
                model=self.model,
                api_key=self.apiKey,
                messages=messages,
                max_tokens=4000,
                stream=True,
            )
        except Exception as e:
            raise Exception(f"Error during AI Response: {e}")
        et = time.time()
        print(f"starting streaming in {et-st} seconds")
        async for chunk in agent_response:
            assesment_chunk = chunk.choices[0].delta.content or ""
            self.response_chunks.append(assesment_chunk)
            yield json.dumps(
                {
                    "chunk": assesment_chunk,
                }
            )

        title_generation_message = [
            {"role": "system", "content": assessment_title_prompt},
            {"role": "user", "content": query},
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
        title_to_save = title_to_save.strip('"')

        try:
            # add the interaction count
            interaction_manager.add_interaction_Assesment(user_id)

            # Storing assesment response to database
            remote_storage.add_assesment(
                assesment_id=assesment_id,
                user_query=query,
                assesment_response=self.get_complete_assesment_response(),
                user_id=user_id,
                summary_title=title_to_save,
            )

            # # Generate suggested prompts and append to the generation response
            # complete_response = self.get_complete_assesment_response()
            # suggested_prompts = await self.generate_suggested_prompts(complete_response)
            # yield json.dumps(
            #     {
            #         "suggested_prompts": suggested_prompts,
            #     }
            # )
        except Exception as e:
            raise Exception(f"Error storing assessment: {e}")

    def get_complete_assesment_response(self) -> str:
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

    # Added another function so that the lesson planner can translate text to a particular response.
    async def translate(
        self,
        text: str,
        table_name: str,
        assessment_id: str,
        target_language: str,
        remote_storage: SupabaseStorage,
    ):
        print("generating translation....")
        st = time.time()
        translation_id = self.generate_assesment_id()
        # Check and regenerate translation_id if it matches assessment_id
        while translation_id == assessment_id:
            print(
                f"regenerating translation_id as it matches assessment_id {assessment_id}"
            )
            translation_id = self.generate_assesment_id()

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

        translated_text = self.get_complete_assesment_response()
        try:
            # Storing assesment response to database
            remote_storage.add_assesment_quick_action(
                action_id=translation_id,
                action_query=action_query,
                action_response=translated_text,
                original_id=assessment_id,
                action_type="Translate",
                table_name=table_name,
            )

        except Exception as e:
            raise Exception(f"Error storing translating text: {e}")


class Assessmentchat:
    def __init__(self) -> None:
        self.storage = SupabaseStorage()  # Initialize Supabase storage
        self.chat_messages = [{"role": "system", "content": extended_chat_prompt}]
        self.response_queue = asyncio.Queue()
        self.response_chunks = []

    def generate_assessment_chat_id(self) -> str:
        return str(uuid.uuid4())

    def get_complete_response(self) -> str:
        return "".join([chunk for chunk in self.response_chunks])

    async def chat(
        self,
        query: str,
        assessment_history_id: str,
        agent_details: Dict[str, Any],
        chat_id: Optional[str] = None,
    ):
        chat_msg_track = 0
        if chat_id is None:
            chat_id = self.generate_assessment_chat_id()
            print(f"generating chat with id {chat_id}")
            chat_msg_track += 1

        await self.response_queue.put(json.dumps({"id": chat_id}))

        # Fetch the context list
        context = self.storage.get_context_list(assessment_history_id, agent_details)

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
            self.storage.store_edited_response_assessment_chat(
                chat_id=chat_id,
                user_msg=query,
                chat_response=complete_response,
            )
        else:
            self.storage.add_assessment_chat(
                chat_msg_id=chat_id,
                user_query=query,
                chat_response=complete_response,
                assessment_history_id=assessment_history_id,
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


def get_assesment_generator() -> AssesmentGenerator:
    return AssesmentGenerator(
        apiKey=os.getenv("AZURE_API_KEY"), model=os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o")
    )
