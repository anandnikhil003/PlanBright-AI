import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
)
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import VectorStoreIndex
from config.azure_provider import (
    azure_api_key,
    azure_api_version,
    azure_embedding_deployment,
    azure_endpoint,
)


load_dotenv()

class DocumentLoader:
    def load_documents(self, file_path):
        return SimpleDirectoryReader(input_files=[file_path]).load_data()


class QueryEngineFactory:
    def create_query_engine(self, documents):
        embed_model = AzureOpenAIEmbedding(
            deployment_name=azure_embedding_deployment(),
            api_key=azure_api_key(),
            azure_endpoint=azure_endpoint(),
            api_version=azure_api_version(),
        )
        splitter = SemanticSplitterNodeParser(
            buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
        )

        nodes = splitter.get_nodes_from_documents(documents)
        vector_index = VectorStoreIndex(nodes)
        query_engine = vector_index.as_query_engine(streaming=True, similarity_top_k=1)

        return query_engine


class QueryEngineTester:
    def test_query_engine(self, query_engine, question):
        response = query_engine.query(question)
        return response


def process_pdf(file_path):
    document_loader = DocumentLoader()
    documents = document_loader.load_documents(file_path)

    query_engine_factory = QueryEngineFactory()
    query_engine = query_engine_factory.create_query_engine(documents)

    return query_engine


def ask_question(query_engine, question):
    query_engine_tester = QueryEngineTester()
    response_final = query_engine_tester.test_query_engine(query_engine, question)
    return response_final


# Example usage
# pdf_processor = process_pdf("E:/Aistra/unconstrained-bot-backend/data_ingestion/pdf_data/school-doc/mlpdf.pdf")


# Run the event loop
# asyncio.run(main())
