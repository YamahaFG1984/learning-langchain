from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import InMemorySaver


class State(TypedDict):
    messages: Annotated[list, add_messages]


builder = StateGraph(State)

model = ChatOpenAI(model="gpt-4.1-mini")


def chatbot(state: State):
    answer = model.invoke(state["messages"])
    return {"messages": [answer]}


builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# Add persistence with InMemorySaver
graph = builder.compile(checkpointer=InMemorySaver())

# Configure thread
thread1 = {"configurable": {"thread_id": "1"}}

# Run with persistence
result_1 = graph.invoke({"messages": [HumanMessage("hi, my name is Jack!")]}, thread1)
print(result_1)

result_2 = graph.invoke({"messages": [HumanMessage("what is my name?")]}, thread1)
print(result_2)

# Get state
print(graph.get_state(thread1))
