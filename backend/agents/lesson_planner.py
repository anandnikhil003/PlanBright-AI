import os
import time
import uuid
import json
import asyncio
import pandas as pd
from dotenv import load_dotenv
from config.azure_provider import completion, acompletion
from db.remote_storage import SupabaseStorage
from db.interaction_manager import InteractionManager
from prompts.bot_prompts import (
    expand_lesson_plan_prompt,
    lesson_planner_strategy,
    lesson_plan_title_prompt,
)
from typing import Optional, Dict, Any
from config.action_items_agents import ActionAgents
from prompts.bot_prompts import extended_chat_prompt

load_dotenv()


def get_lesson_plan_examples() -> str:
    examples = """"""
    example_template = """
        Example {index}
        User-Query: {query}
        Lesson Plan: 
        {lesson_plan}
        --------------------------------------------
    """
    file_name = os.path.join("data", "lesson_planner", "lesson_plan_examples.csv")
    df = pd.read_csv(file_name)
    for index, row in df.iterrows():
        example = example_template.format(
            index=index + 1, query=row["user_query"], lesson_plan=row["lesson_plan"]
        )
        examples += example
    return examples


def get_diff_strategies() -> str:
    file_name = os.path.join("data", "lesson_planner", "teaching_strategies.csv")
    df = pd.read_csv(file_name)
    return df.to_markdown(index=True)


lesson_planner_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_lesson_plan_examples",
            "description": "Get relevant lesson plan examples",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_diff_strategies",
            "description": "Get recommended differentiation strategies",
        },
    },
]

available_functions = {
    "get_lesson_plan_examples": get_lesson_plan_examples,
    "get_diff_strategies": get_diff_strategies,
}


class LessonPlanner(ActionAgents):
    def __init__(
        self,
        apiKey: str,
        model: str,
    ) -> None:
        self.model = model
        self.apiKey = apiKey
        self.response_chunks = []

    def generate_lesson_plan_id(self) -> str:
        return str(uuid.uuid4())

    async def stream_and_save_lesson_plan(
        self,
        query: str,
        remote_storage: SupabaseStorage,
        user_id: str,
        interaction_manager: InteractionManager,
    ):
        """
        Generate a lesson plan based on the given query and optionally stream the response.

        Args:
            query (str): The query for generating the lesson plan.
        """

        lesson_plan_id = self.generate_lesson_plan_id()
        print(f"generating lesson plan with id {lesson_plan_id}")
        yield json.dumps({"id": lesson_plan_id})
        await asyncio.sleep(0.02)  # wait for 20ms
        messages = [
            {"role": "system", "content": lesson_planner_strategy},
            {"role": "user", "content": query},
        ]
        st = time.time()
        try:
            agent_response = await acompletion(
                model=self.model,
                api_key=self.apiKey,
                messages=messages,
                tools=lesson_planner_tools,
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
                max_tokens=3000,
                stream=True,
            )
        except Exception as e:
            raise Exception(f"Error during AI Response: {e}")
        et = time.time()
        print(f"starting streaming in {et-st} seconds")
        async for chunk in agent_response:
            plan_chunk = chunk.choices[0].delta.content or ""
            self.response_chunks.append(plan_chunk)
            # print("Received Chunk:", plan_chunk)
            yield json.dumps(
                {
                    "chunk": plan_chunk,
                }
            )

        title_generation_message = [
            {"role": "system", "content": lesson_plan_title_prompt},
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
            interaction_manager.add_interaction_Lesson_Plan(user_id)

            # store the lesson plan for metrics
            remote_storage.add_lesson_plan(
                lesson_plan_id=lesson_plan_id,
                user_query=query,
                lesson_plan=self.get_complete_lesson_plan(),
                user_id=user_id,
                summary_title=title_to_save,
            )

            # # Generate suggested prompts and append to the generation response
            # complete_response = self.get_complete_lesson_plan()
            # suggested_prompts = await self.generate_suggested_prompts(complete_response)
            # yield json.dumps(
            #     {
            #         "suggested_prompts": suggested_prompts,
            #     }
            # )
        except Exception as e:
            raise Exception(f"Error storing lesson plan: {e}")

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

    def get_complete_lesson_plan(self) -> str:
        return "".join([chunk for chunk in self.response_chunks])

    def generate_expanded_response(self, query: str, lesson_plan: str) -> str:
        messages = [
            {"role": "system", "content": expand_lesson_plan_prompt},
            {"role": "assistant", "content": lesson_plan},
            {"role": "user", "content": query},
        ]
        st = time.time()
        agent_response = completion(
            model=self.model, api_key=self.apiKey, messages=messages
        )
        et = time.time()
        print(f"response expanded in {et-st} seconds")
        return agent_response.choices[0].message.content

    async def translate(
        self,
        text: str,
        table_name: str,
        lessonplan_id: str,
        target_language: str,
        remote_storage: SupabaseStorage,
    ):
        print("generating translation....")
        st = time.time()
        translation_id = self.generate_lesson_plan_id()
        # Check and regenerate translation_id if it matches lessonplan_id
        while translation_id == lessonplan_id:
            print(
                f"regenerating translation_id as it matches lessonplan_id {lessonplan_id}"
            )
            translation_id = self.generate_lesson_plan_id()

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

        translated_text = self.get_complete_lesson_plan()
        try:
            # Storing lessonplan response to database
            remote_storage.add_lessonplan_quick_action(
                action_id=translation_id,
                action_query=action_query,
                action_response=translated_text,
                original_id=lessonplan_id,
                action_type="Translate",
                table_name=table_name,
            )

        except Exception as e:
            raise Exception(f"Error storing lessonplan: {e}")


class LessonPlannerChat:
    def __init__(self) -> None:
        self.storage = SupabaseStorage()  # Initialize Supabase storage
        self.chat_messages = [{"role": "system", "content": extended_chat_prompt}]
        self.response_queue = asyncio.Queue()
        self.response_chunks = []

    def generate_lesson_plan_chat_id(self) -> str:
        return str(uuid.uuid4())

    def get_complete_response(self) -> str:
        return "".join([chunk for chunk in self.response_chunks])

    async def chat(
        self,
        query: str,
        lesson_history_id: str,
        agent_details: Dict[str, Any],
        chat_id: Optional[str] = None,
    ):
        chat_msg_track = 0
        if chat_id is None:
            chat_id = self.generate_lesson_plan_chat_id()
            print(f"generating chat with id {chat_id}")
            chat_msg_track += 1

        await self.response_queue.put(json.dumps({"id": chat_id}))

        # Fetch the context list
        context = self.storage.get_context_list(lesson_history_id, agent_details)

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
            self.storage.store_edited_response_lesson_plan_chat(
                chat_id=chat_id,
                user_msg=query,
                chat_response=complete_response,
            )
        else:
            self.storage.add_lesson_plan_chat(
                chat_msg_id=chat_id,
                user_query=query,
                chat_response=complete_response,
                lesson_history_id=lesson_history_id,
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


def get_lesson_planner() -> LessonPlanner:
    return LessonPlanner(apiKey=os.getenv("AZURE_API_KEY"), model=os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o"))
