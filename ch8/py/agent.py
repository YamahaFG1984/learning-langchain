"""Shared agent used by the Chapter 8 examples.

This is the "dealing with many tools" architecture from Chapter 6: a RAG step
picks the most relevant tools for the query, then the usual model <-> tools loop
runs. Every example in this chapter imports `build_graph` from here.
"""

import ast

from typing import Annotated, TypedDict

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.vectorstores.in_memory import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


@tool
def calculator(query: str) -> str:
    """A simple calculator tool. Input should be a mathematical expression."""
    return ast.literal_eval(query)


search = DuckDuckGoSearchRun()
tools = [search, calculator]

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
model = ChatOpenAI(model="gpt-4.1-mini", temperature=0.1)

tools_retriever = InMemoryVectorStore.from_documents(
    [Document(t.description, metadata={"name": t.name}) for t in tools],
    embeddings,
).as_retriever()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    selected_tools: list[str]


def select_tools(state: State) -> State:
    query = state["messages"][-1].content
    tool_docs = tools_retriever.invoke(query)
    return {"selected_tools": [doc.metadata["name"] for doc in tool_docs]}


def model_node(state: State) -> State:
    selected = [t for t in tools if t.name in state["selected_tools"]]
    res = model.bind_tools(selected).invoke(state["messages"])
    return {"messages": res}


def build_graph(checkpointer=None):
    """Build (and compile) the agent graph, optionally with persistence."""
    builder = StateGraph(State)
    builder.add_node("select_tools", select_tools)
    builder.add_node("model", model_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "select_tools")
    builder.add_edge("select_tools", "model")
    builder.add_conditional_edges("model", tools_condition)
    builder.add_edge("tools", "model")
    return builder.compile(checkpointer=checkpointer)


QUESTION = "How old was the 30th president of the United States when he died?"
