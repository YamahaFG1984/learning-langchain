"""Supervisor multi-agent architecture (Chapter 7).

A supervisor node uses structured output to decide which worker agent runs next,
or whether the work is FINISHed. Requires langchain>=1.0 and langgraph>=1.0.
"""

from typing import Literal

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel

# The set of workers the supervisor can delegate to.
# Give them self-explanatory names: the LLM only sees the names.
agents = ["researcher", "coder"]


class SupervisorDecision(BaseModel):
    """Who should act next, or FINISH when the task is done."""

    next: Literal["researcher", "coder", "FINISH"]


model = ChatOpenAI(model="gpt-4.1", temperature=0)
supervisor_model = model.with_structured_output(SupervisorDecision)

system_prompt_part_1 = f"""You are a supervisor tasked with managing a conversation
between the following workers: {agents}. Given the following user request,
respond with the worker to act next. Each worker will perform a task and respond
with their results and status. When finished, respond with FINISH."""

system_prompt_part_2 = (
    "Given the conversation above, who should act next? "
    f"Or should we FINISH? Select one of: {', '.join(agents)}, FINISH"
)


class AgentState(MessagesState):
    """Shared state: the message history plus the supervisor's routing decision."""

    next: str


def supervisor(state: AgentState) -> dict:
    messages = [
        {"role": "system", "content": system_prompt_part_1},
        *state["messages"],
        {"role": "system", "content": system_prompt_part_2},
    ]
    decision = supervisor_model.invoke(messages)
    # A node must return a state update, so wrap the decision in the `next` key.
    return {"next": decision.next}


def researcher(state: AgentState) -> dict:
    response = model.invoke(
        [
            {
                "role": "system",
                "content": "You are a research assistant. Analyze the request and "
                "provide relevant information. Be concise.",
            },
            *state["messages"],
        ]
    )
    return {"messages": [response]}


def coder(state: AgentState) -> dict:
    response = model.invoke(
        [
            {
                "role": "system",
                "content": "You are a coding assistant. Implement the requested "
                "functionality. Be concise.",
            },
            *state["messages"],
        ]
    )
    return {"messages": [response]}


def route(state: AgentState) -> Literal["researcher", "coder", "__end__"]:
    """Map the supervisor's decision onto a node name (or the end of the graph)."""
    return END if state["next"] == "FINISH" else state["next"]


builder = StateGraph(AgentState)
builder.add_node("supervisor", supervisor)
builder.add_node("researcher", researcher)
builder.add_node("coder", coder)

builder.add_edge(START, "supervisor")
# Route to one of the agents, or exit, based on the supervisor's decision.
builder.add_conditional_edges("supervisor", route, ["researcher", "coder", END])
builder.add_edge("researcher", "supervisor")
builder.add_edge("coder", "supervisor")

graph = builder.compile()

if __name__ == "__main__":
    initial_state = {
        "messages": [
            {
                "role": "user",
                "content": "I need help analyzing some data and creating a visualization.",
            }
        ]
    }

    for step in graph.stream(initial_state):
        for node, update in step.items():
            print(f"\n--- {node} ---")
            if "next" in update:
                print("next:", update["next"])
            if update.get("messages"):
                print(update["messages"][-1].content[:200], "...")
