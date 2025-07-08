import os
from dotenv import load_dotenv
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage, RemoveMessage
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from src.tools.arithmetic import add, subtract, multiply, divide

# Load env variables
load_dotenv()

# Tools
tavily_search_tool = TavilySearch(max_results=2)
tools = [tavily_search_tool, add, subtract, multiply, divide]

# State
class State(MessagesState):
    # Add additional keys beyond the built in messages
    pass

# Following is what the built in Langgraph MessagesState is
# class MessagesState(TypedDict):
#     messages: Annotated[list[AnyMessage], add_messages]

# LLM
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

# System Prompt
sys_msg = SystemMessage(content="You are a helpful assistant!")

# Node
def assistant(state: State):
      return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("assistant", assistant)
graph_builder.add_node("tools", ToolNode(tools))

graph_builder.add_edge(START, "assistant")
graph_builder.add_conditional_edges("assistant", tools_condition)
graph_builder.add_edge("tools", "assistant")

# # Compile Graph Witout Memory
# graph = graph_builder.compile()

# Compile Graph with memory
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Specify a thread
# config = {"configurable": {"thread_id": "1"}}

# # Input
# messages = [HumanMessage("Add 3 and 4")]

# # Run
# messages = graph.invoke({"messages": messages}, config)
# for m in messages:
#     m.pretty_print()

# Stream Graph updates
# def stream_graph_updates(user_input: str):
#     # for event in graph.stream({"messages": [{ "role": "user", "content": user_input }]}):
#     #     for value in event.values():
#     #         print("Assistant:", value["messages"][-1].content)
#     events = graph.stream(
#         {"messages": [{"role": "user", "content": user_input}]},
#         config,
#         stream_mode="values"
#     )
#     for event in events:
#         event["messages"][-1].pretty_print()

# # Run Graph
# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Exiting...")
#             break
#         stream_graph_updates(user_input)
#     except:
#         user_input = "Tell me something about LangGraph?"
#         print("User: " + user_input)
#         stream_graph_updates(user_input)
#         break