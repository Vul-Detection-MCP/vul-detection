import os

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()
load_dotenv(os.getenv("PROJECT_ENV_ADDITIONAL_ABS_FILE"))


async def create_tools():
    client = MultiServerMCPClient(
        {
            "vulnerability_detector": {
                "transport": "http",
                "url": f"http://{os.getenv("CONTAINER_MCP_SERVER_HOST")}:{os.getenv("CONTAINER_MCP_SERVER_PORT")}/mcp",
            }
        }
    )
    return await client.get_tools()


def create_chatgpt(model):
    return ChatOpenAI(
        model=model,
        api_key=os.getenv("OPENAI_API_KEY")
    )


def create_ollama(model):
    return ChatOllama(
        model=model,
        base_url=f"http://{os.getenv("OTHER_LLM_BASE_URL")}"
    )
