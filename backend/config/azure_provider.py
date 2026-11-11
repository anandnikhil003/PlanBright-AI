"""Shared Azure OpenAI configuration for LiteLLM and OpenAI SDK clients."""

import os
from urllib.parse import parse_qs, urlsplit

from dotenv import load_dotenv
from litellm import acompletion as _litellm_acompletion
from litellm import completion as _litellm_completion
from openai import AzureOpenAI

load_dotenv()


def azure_endpoint() -> str:
    value = os.getenv("AZURE_API_BASE", "").strip().strip("\"'").rstrip("/")
    if not value:
        value = os.getenv("BRIDGE_AZURE_OPENAI_URL", "").strip().strip("\"'")
    if not value:
        raise RuntimeError(
            "Set AZURE_API_BASE or BRIDGE_AZURE_OPENAI_URL in backend/.env"
        )
    parsed = urlsplit(value)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError("AZURE_API_BASE must be an HTTPS Azure endpoint URL")
    # Accept either the resource root or a pasted deployment URL; SDKs need the root.
    return f"{parsed.scheme}://{parsed.netloc}"


def azure_api_key() -> str:
    value = os.getenv("AZURE_API_KEY", "").strip()
    if not value:
        raise RuntimeError("AZURE_API_KEY is not set in backend/.env")
    return value


def azure_chat_deployment() -> str:
    configured = os.getenv("AZURE_CHAT_DEPLOYMENT", "").strip()
    if configured:
        return configured
    bridge_url = os.getenv("BRIDGE_AZURE_OPENAI_URL", "").strip().strip("\"'")
    path_parts = [part for part in urlsplit(bridge_url).path.split("/") if part]
    try:
        return path_parts[path_parts.index("deployments") + 1]
    except (ValueError, IndexError):
        return "gpt-4o"


def azure_embedding_deployment() -> str:
    value = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "").strip()
    if not value:
        raise RuntimeError(
            "AZURE_EMBEDDING_DEPLOYMENT must name a deployed Azure embedding model"
        )
    return value


def azure_api_version() -> str:
    configured = os.getenv("AZURE_API_VERSION", "").strip()
    if configured:
        return configured
    bridge_url = os.getenv("BRIDGE_AZURE_OPENAI_URL", "").strip().strip("\"'")
    query = parse_qs(urlsplit(bridge_url).query)
    return query.get("api-version", ["2024-12-01-preview"])[0].rstrip("'")


def azure_openai_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=azure_api_key(),
        azure_endpoint=azure_endpoint(),
        api_version=azure_api_version(),
    )


def _azure_litellm_kwargs(kwargs):
    kwargs = dict(kwargs)
    kwargs["model"] = f"azure/{azure_chat_deployment()}"
    kwargs["api_key"] = azure_api_key()
    kwargs["api_base"] = azure_endpoint()
    kwargs["api_version"] = azure_api_version()
    return kwargs


async def acompletion(*args, **kwargs):
    return await _litellm_acompletion(*args, **_azure_litellm_kwargs(kwargs))


def completion(*args, **kwargs):
    return _litellm_completion(*args, **_azure_litellm_kwargs(kwargs))
