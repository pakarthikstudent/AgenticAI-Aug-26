import asyncio

from dotenv import load_dotenv

# Groq LLM
from langchain_groq import ChatGroq

# MCP Client
from langchain_mcp_adapters.client import MultiServerMCPClient

# LangGraph
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition


# Load .env file
load_dotenv()


async def main():

    # ---------------------------------------
    # 1. Create MCP Client
    # ---------------------------------------

    client = MultiServerMCPClient(
        {
            "customer_server": {
                "command": "python",
                "args": ["mcp_server.py"],
                "transport": "stdio"
            }
        }
    )


    # ---------------------------------------
    # 2. Load MCP Tools
    # ---------------------------------------

    tools = await client.get_tools()

    print("\nAvailable MCP Tools:")

    for tool in tools:
        print("-", tool.name)


    # ---------------------------------------
    # 3. Create Groq LLM
    # ---------------------------------------

    llm = ChatGroq(
        model="qwen/qwen3.6-27b",
        temperature=0
    )


    # ---------------------------------------
    # 4. Bind MCP Tools to Groq
    # ---------------------------------------

    llm_with_tools = llm.bind_tools(tools)


    # ---------------------------------------
    # 5. Agent Node
    # ---------------------------------------

    async def call_model(state: MessagesState):

        response = await llm_with_tools.ainvoke(
            state["messages"]
        )

        return {
            "messages": [response]
        }


    # ---------------------------------------
    # 6. Create LangGraph
    # ---------------------------------------

    builder = StateGraph(MessagesState)


    # Add Agent Node
    builder.add_node(
        "agent",
        call_model
    )


    # Add Tool Node
    builder.add_node(
        "tools",
        ToolNode(tools)
    )


    # START → AGENT
    builder.add_edge(
        START,
        "agent"
    )


    # AGENT → TOOLS or END
    builder.add_conditional_edges(
        "agent",
        tools_condition
    )


    # TOOLS → AGENT
    builder.add_edge(
        "tools",
        "agent"
    )


    # Compile Graph
    graph = builder.compile()


    # ---------------------------------------
    # 7. Ask User Question
    # ---------------------------------------

    result = await graph.ainvoke(
        {
            "messages": [
                (
                    "user",
                    "Get customer 101 and show all their orders"
                )
            ]
        }
    )


    # ---------------------------------------
    # 8. Print Result
    # ---------------------------------------

    print("\nFINAL ANSWER:\n")

    print(
        result["messages"][-1].content
    )


# ---------------------------------------
# Run Application
# ---------------------------------------

if __name__ == "__main__":
    asyncio.run(main())