"""Resume an interrupted graph by invoking it again with `None` as the input."""

import asyncio

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agent import QUESTION, build_graph


async def main():
    graph = build_graph(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "1"}}

    # 1. Run until we are about to call a tool.
    async for c in graph.astream(
        {"messages": [HumanMessage(QUESTION)]}, config, interrupt_before=["tools"]
    ):
        print(c)

    print("\n--- approved, resuming ---\n")

    # 2. `None` input means "continue where you left off" for this thread.
    async for c in graph.astream(None, config):
        print(c)


if __name__ == "__main__":
    asyncio.run(main())
