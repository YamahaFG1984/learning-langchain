"""Fork: browse the history of past states and replay one of them."""

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agent import QUESTION, build_graph


def main():
    graph = build_graph(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "1"}}

    for c in graph.stream({"messages": [HumanMessage(QUESTION)]}, config):
        print(c)

    # Most recent state first, oldest last.
    history = list(graph.get_state_history(config))
    print("\nHistory states:", len(history))
    for i, state in enumerate(history):
        print(i, "next:", state.next)

    # Replay from a past checkpoint: passing that checkpoint's config forks the
    # thread, so the original run is kept alongside the new one.
    if len(history) >= 3:
        print("\n--- replaying from history[2] ---\n")
        result = graph.invoke(None, history[2].config)
        print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
