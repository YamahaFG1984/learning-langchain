"""Inspect and edit the state of a paused graph before resuming it."""

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agent import QUESTION, build_graph


def main():
    graph = build_graph(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "1"}}

    # Run up to the tools node.
    for c in graph.stream(
        {"messages": [HumanMessage(QUESTION)]}, config, interrupt_before=["tools"]
    ):
        print(c)

    state = graph.get_state(config)
    print("\nCurrent state next node:", state.next)

    # Rewrite the search query the model chose, then resume with our version.
    last = state.values["messages"][-1]
    if last.tool_calls:
        edited = last.model_copy(deep=True)
        edited.tool_calls[0]["args"]["query"] = "Calvin Coolidge age at death"
        # Messages are merged by id, so re-writing the same id replaces it.
        graph.update_state(config, {"messages": [edited]})
        print("Edited tool call:", graph.get_state(config).values["messages"][-1].tool_calls)

    for c in graph.stream(None, config):
        print(c)


if __name__ == "__main__":
    main()
