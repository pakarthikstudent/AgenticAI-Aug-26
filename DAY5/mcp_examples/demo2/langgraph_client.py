import asyncio

from dotenv import load_dotenv

# Groq
from langchain_groq import ChatGroq

# MCP
from langchain_mcp_adapters.client import MultiServerMCPClient

# LangGraph
from langgraph.graph import (
    StateGraph,
    MessagesState,
    START
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition
)


# -------------------------------------
# Load Environment Variables
# -------------------------------------

load_dotenv()


async def main():

    # ---------------------------------
    # 1. Connect to MCP Server
    # ---------------------------------

    client = MultiServerMCPClient(
        {
            "oracle_server": {

                "command": "python",

                "args": [
                    "mcp_oracle_server.py"
                ],

                "transport": "stdio"
            }
        }
    )


    # ---------------------------------
    # 2. Get MCP Tools
    # ---------------------------------

    tools = await client.get_tools()


    print("\nAvailable MCP Tools:")

    for tool in tools:

        print("-", tool.name)


    # ---------------------------------
    # 3. Create Groq LLM
    # ---------------------------------

    llm = ChatGroq(

        model="qwen/qwen3.6-27b",

        temperature=0
    )


    # ---------------------------------
    # 4. Bind MCP Tools
    # ---------------------------------

    llm_with_tools = llm.bind_tools(
        tools
    )


    # ---------------------------------
    # 5. Agent Node
    # ---------------------------------

    async def agent(state: MessagesState):

        response = await llm_with_tools.ainvoke(
            state["messages"]
        )

        return {
            "messages": [
                response
            ]
        }


    # ---------------------------------
    # 6. Build LangGraph
    # ---------------------------------

    graph_builder = StateGraph(
        MessagesState
    )


    # Agent Node
    graph_builder.add_node(
        "agent",
        agent
    )


    # Tool Node
    graph_builder.add_node(
        "tools",
        ToolNode(tools)
    )


    # START → AGENT

    graph_builder.add_edge(
        START,
        "agent"
    )


    # AGENT → TOOLS or END

    graph_builder.add_conditional_edges(
        "agent",
        tools_condition
    )


    # TOOLS → AGENT

    graph_builder.add_edge(
        "tools",
        "agent"
    )


    # ---------------------------------
    # 7. Compile Graph
    # ---------------------------------

    app = graph_builder.compile()


    # ---------------------------------
    # 8. User Question
    # ---------------------------------

    result = await app.ainvoke(

        {
            "messages": [

                (
                    "user",

                    """
                    Show me all products
                    in the products table.
                    """
                )

            ]
        }
    )


    # ---------------------------------
    # 9. Final Answer
    # ---------------------------------

    print("\nFINAL ANSWER:\n")

    print(
        result["messages"][-1].content
    )


# -------------------------------------
# Run
# -------------------------------------

if __name__ == "__main__":

    asyncio.run(main())
