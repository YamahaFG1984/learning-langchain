from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


builder = StateGraph(State)

model = ChatOpenAI(model="gpt-4.1-mini")


def chatbot(state: State):
    answer = model.invoke(state["messages"])
    return {"messages": [answer]}


# Add the chatbot node
builder.add_node("chatbot", chatbot)

# Add edges
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile()

# Run the graph
input = {"messages": [HumanMessage("hi!")]}
for chunk in graph.stream(input):
    print(chunk)
