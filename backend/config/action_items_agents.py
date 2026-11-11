from config.azure_provider import acompletion
import time
import json


# Abstracted Action Agents class which all agents will inherit these class functionalities
# This includes summarizing as bulletpoints, paragraphs, making it shorter, simpler, longer and more professional
class ActionAgents:
    async def summarize_as_bulletpoints(
        self,
        text: str,
        table_name: str,
        response_id: str,
        storage_method: callable,
        unique_id_creator: callable,
        complete_response: callable,
    ):
        print("generating summarize as bulletpoints....")
        st = time.time()
        summarize_as_bulletpoints_id = unique_id_creator()
        # Check and regenerate translation_id if it matches assessment_id
        while summarize_as_bulletpoints_id == response_id:
            print(
                f"regenerating summarize_as_bulletpoints_id as it matches response_id {response_id}"
            )
            summarize_as_bulletpoints_id = unique_id_creator()

        print(
            f"generating summarize as bulletpoints with id {summarize_as_bulletpoints_id}"
        )
        yield json.dumps({"id": summarize_as_bulletpoints_id})
        summary_prompt = f"Please rewrite the following response in a summarized manner with bullet points, keeping it's context and important details intact:\n\n{text}"
        action_query = "Summarize it in points."
        agent_response = await acompletion(
            model=self.model,
            api_key=self.apiKey,
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=4000,
            stream=True,
        )
        et = time.time()
        print(f"starting streaming in {et-st} seconds")

        async for chunk in agent_response:
            summarized_text_chunk = chunk.choices[0].delta.content or ""
            self.response_chunks.append(summarized_text_chunk)
            yield json.dumps(
                {
                    "chunk": summarized_text_chunk,
                }
            )
        summarized_text = complete_response()
        try:
            # Storing assesment response to database
            storage_method(
                action_id=summarize_as_bulletpoints_id,
                action_query=action_query,
                action_response=summarized_text,
                original_id=response_id,
                action_type="Summarize as Bulletpoints",
                table_name=table_name,
            )

        except Exception as e:
            raise Exception(f"Error storing assessment: {e}")

    async def summarize_as_paragraphs(
        self,
        text: str,
        table_name: str,
        response_id: str,
        storage_method: callable,
        unique_id_creator: callable,
        complete_response: callable,
    ):
        print("generating summarize as paragraphs....")
        st = time.time()
        summarize_as_paragraphs_id = unique_id_creator()
        # Check and regenerate translation_id if it matches assessment_id
        while summarize_as_paragraphs_id == response_id:
            print(
                f"regenerating summarize_as_paragraphs_id as it matches response_id {response_id}"
            )
            summarize_as_paragraphs_id = unique_id_creator()

        print(
            f"generating summarize as paragraphs with id {summarize_as_paragraphs_id}"
        )
        yield json.dumps({"id": summarize_as_paragraphs_id})
        summary_prompt = f"Please rewrite the following response in a summarized manner in paragraphs, keeping it's context and important details intact:\n\n{text}"
        action_query = "Summarize it in paragraph."
        agent_response = await acompletion(
            model=self.model,
            api_key=self.apiKey,
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=4000,
            stream=True,
        )
        et = time.time()
        print(f"starting streaming in {et-st} seconds")

        async for chunk in agent_response:
            summarized_text_chunk = chunk.choices[0].delta.content or ""
            self.response_chunks.append(summarized_text_chunk)
            yield json.dumps(
                {
                    "chunk": summarized_text_chunk,
                }
            )
        summarized_text = complete_response()
        try:
            # Storing assesment response to database
            storage_method(
                action_id=summarize_as_paragraphs_id,
                action_query=action_query,
                action_response=summarized_text,
                original_id=response_id,
                action_type="Summarize as Paragraphs",
                table_name=table_name,
            )

        except Exception as e:
            raise Exception(f"Error storing assessment: {e}")

    async def make_simpler(
        self,
        text: str,
        table_name: str,
        response_id: str,
        storage_method: callable,
        unique_id_creator: callable,
        complete_response: callable,
    ):
        print("generating simpler response....")
        st = time.time()
        simplified_id = unique_id_creator()
        # Check and regenerate translation_id if it matches assessment_id
        while simplified_id == response_id:
            print(f"regenerating simplified_id as it matches response_id {response_id}")
            simplified_id = unique_id_creator()

        print(f"generating simpler response with id {simplified_id}")
        yield json.dumps({"id": simplified_id})
        summary_prompt = f"Please rewrite the following response but simplify the response, keeping the context and structure of the document the same:\n\n{text}"
        action_query = "Make it simpler"
        agent_response = await acompletion(
            model=self.model,
            api_key=self.apiKey,
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=4000,
            stream=True,
        )
        et = time.time()
        print(f"starting streaming in {et-st} seconds")

        async for chunk in agent_response:
            simpler_text_chunk = chunk.choices[0].delta.content or ""
            self.response_chunks.append(simpler_text_chunk)
            yield json.dumps(
                {
                    "chunk": simpler_text_chunk,
                }
            )
        simpler_text = complete_response()
        try:
            # Storing assesment response to database
            storage_method(
                action_id=simplified_id,
                action_query=action_query,
                action_response=simpler_text,
                original_id=response_id,
                action_type="Make Simpler",
                table_name=table_name,
            )

        except Exception as e:
            raise Exception(f"Error storing assessment: {e}")

    async def make_shorter(
        self,
        text: str,
        table_name: str,
        response_id: str,
        storage_method: callable,
        unique_id_creator: callable,
        complete_response: callable,
    ):
        print("generating shorter response....")
        st = time.time()
        shorter_id = unique_id_creator()
        # Check and regenerate translation_id if it matches assessment_id
        while shorter_id == response_id:
            print(f"regenerating shorter_id as it matches response_id {response_id}")
            shorter_id = unique_id_creator()

        print(f"generating shorter response with id {shorter_id}")
        yield json.dumps({"id": shorter_id})
        summary_prompt = f"Please rewrite the following response but make it shorter, keeping the context and structure of the document the same:\n\n{text}"
        action_query = "Make it shorter"
        agent_response = await acompletion(
            model=self.model,
            api_key=self.apiKey,
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=4000,
            stream=True,
        )
        et = time.time()
        print(f"starting streaming in {et-st} seconds")

        async for chunk in agent_response:
            shorter_text_chunk = chunk.choices[0].delta.content or ""
            self.response_chunks.append(shorter_text_chunk)
            yield json.dumps(
                {
                    "chunk": shorter_text_chunk,
                }
            )
        shorter_text = complete_response()
        try:
            # Storing assesment response to database
            storage_method(
                action_id=shorter_id,
                action_query=action_query,
                action_response=shorter_text,
                original_id=response_id,
                action_type="Make Shorter",
                table_name=table_name,
            )

        except Exception as e:
            raise Exception(f"Error storing assessment: {e}")

    async def make_longer(
        self,
        text: str,
        table_name: str,
        response_id: str,
        storage_method: callable,
        unique_id_creator: callable,
        complete_response: callable,
    ):
        print("generating longer response....")
        st = time.time()
        longer_id = unique_id_creator()
        # Check and regenerate translation_id if it matches assessment_id
        while longer_id == response_id:
            print(f"regenerating longer_id as it matches response_id {response_id}")
            longer_id = unique_id_creator()

        print(f"generating longer response with id {longer_id}")
        yield json.dumps({"id": longer_id})
        summary_prompt = f"Please rewrite the following response but make it longer, adding more relevant details and keeping the context and structure of the document the same:\n\n{text}"
        action_query = "Make it longer"
        agent_response = await acompletion(
            model=self.model,
            api_key=self.apiKey,
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=4000,
            stream=True,
        )
        et = time.time()
        print(f"starting streaming in {et-st} seconds")

        async for chunk in agent_response:
            longer_text_chunk = chunk.choices[0].delta.content or ""
            self.response_chunks.append(longer_text_chunk)
            yield json.dumps(
                {
                    "chunk": longer_text_chunk,
                }
            )
        longer_text = complete_response()
        try:
            # Storing assesment response to database
            storage_method(
                action_id=longer_id,
                action_query=action_query,
                action_response=longer_text,
                original_id=response_id,
                action_type="Make Longer",
                table_name=table_name,
            )

        except Exception as e:
            raise Exception(f"Error storing assessment: {e}")

    async def make_more_professional(
        self,
        text: str,
        table_name: str,
        response_id: str,
        storage_method: callable,
        unique_id_creator: callable,
        complete_response: callable,
    ):
        print("generating professional response....")
        st = time.time()
        professional_id = unique_id_creator()
        # Check and regenerate translation_id if it matches assessment_id
        while professional_id == response_id:
            print(
                f"regenerating professional_id as it matches response_id {response_id}"
            )
            professional_id = unique_id_creator()

        print(f"generating professional response with id {professional_id}")
        yield json.dumps({"id": professional_id})
        summary_prompt = f"Please rewrite the following response in a more professional standard, keeping the context and structure of the document the same:\n\n{text}"
        action_query = "Make it professional"
        agent_response = await acompletion(
            model=self.model,
            api_key=self.apiKey,
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=4000,
            stream=True,
        )
        et = time.time()
        print(f"starting streaming in {et-st} seconds")

        async for chunk in agent_response:
            professional_text_chunk = chunk.choices[0].delta.content or ""
            self.response_chunks.append(professional_text_chunk)
            yield json.dumps(
                {
                    "chunk": professional_text_chunk,
                }
            )
        professional_text = complete_response()
        try:
            # Storing assesment response to database
            storage_method(
                action_id=professional_id,
                action_query=action_query,
                action_response=professional_text,
                original_id=response_id,
                action_type="Make More Professional",
                table_name=table_name,
            )

        except Exception as e:
            raise Exception(f"Error storing assessment: {e}")
