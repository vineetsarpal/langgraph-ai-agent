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
from src.tools.weather import get_weather

# Load env variables
load_dotenv()

# Tools
tavily_search_tool = TavilySearch(max_results=2)
tools = [tavily_search_tool, add, subtract, multiply, divide, get_weather]

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

# Assistant Node
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