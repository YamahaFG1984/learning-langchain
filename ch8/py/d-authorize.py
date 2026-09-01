"""The authorize pattern: pause before a node so a human can approve it."""

import asyncio

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agent import QUESTION, build_graph


async def main():
    graph = build_graph(checkpointer=InMemorySaver())

    input = {"messages": [HumanMessage(QUESTION)]}
    config = {"configurable": {"thread_id": "1"}}

    # Run until the graph is about to enter the `tools` node, then stop.
    async for c in graph.astream(input, config, interrupt_before=["tools"]):
        print(c)

    state = await graph.aget_state(config)
    print("\npaused before:", state.next)
    print("pending tool calls:", state.values["messages"][-1].tool_calls)
    # See e-resume.py for how to continue from here.


if __name__ == "__main__":
    asyncio.run(main())
