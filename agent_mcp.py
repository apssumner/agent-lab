import asyncio
import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

server_params = StdioServerParameters(
    command="python",
    args=["customer_server.py"],
)

async def run_agent(user_message: str):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Ask the MCP server what tools it has -- no hardcoded schema anymore
            tools_response = await session.list_tools()
            tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema,
                }
                for t in tools_response.tools
            ]
            print("Tools discovered from server:", [t["name"] for t in tools])

            messages = [{"role": "user", "content": user_message}]

            response = client.messages.create(  # type: ignore
                model="claude-haiku-4-5",
                max_tokens=1024,
                tools=tools,  # type: ignore
                messages=messages,  # type: ignore
            )

            while response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})  # type: ignore

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        # Call the tool over MCP instead of calling a Python function directly
                        result = await session.call_tool(block.name, block.input)  # type: ignore
                        result_text = result.content[0].text if result.content else "{}" # type: ignore
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        })

                messages.append({"role": "user", "content": tool_results})  # type: ignore

                response = client.messages.create(  # type: ignore
                    model="claude-haiku-4-5",
                    max_tokens=1024,
                    tools=tools,  # type: ignore
                    messages=messages,  # type: ignore
                )

            for block in response.content:
                if block.type == "text":
                    print(block.text)

if __name__ == "__main__":
    asyncio.run(run_agent("If a customer wants to withdraw money from an account that's been inactive for over a year, what should happen?"))