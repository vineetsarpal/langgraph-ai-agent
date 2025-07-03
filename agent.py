import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

load_dotenv()

# Graph State
class State(TypedDict):
    messages: Annotated[list, add_messages]
graph_builder = StateGraph(State)

# Tools
tavily_search_tool = TavilySearch(max_results=2)
tools = [tavily_search_tool]

# Chatbot
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

# Chatbot node
def chatbot(state: State) -> State:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
graph_builder.add_node("chatbot", chatbot)

# Tools node
tool_node = ToolNode(tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)

# Edges
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

# Compile Graph
graph = graph_builder.compile()

# Stream Graph updates
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{ "role": "user", "content": user_input }]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

# Run Graph
while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Exiting...")
            break
        stream_graph_updates(user_input)
    except:
        user_input = "Tell me something about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break