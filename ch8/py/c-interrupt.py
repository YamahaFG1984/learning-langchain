"""The interrupt pattern: stop a running graph from outside it."""

import asyncio
from contextlib import aclosing

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agent import QUESTION, build_graph


async def main():
    # A checkpointer is required: it saves the state after each completed step,
    # so the run can be resumed after being interrupted.
    graph = build_graph(checkpointer=InMemorySaver())

    stop = asyncio.Event()

    input = {"messages": [HumanMessage(QUESTION)]}
    config = {"configurable": {"thread_id": "1"}}

    async def interrupt_after(seconds: float):
        await asyncio.sleep(seconds)
        stop.set()

    asyncio.create_task(interrupt_after(2))

    # `aclosing` makes sure the stream is closed properly when we break out of it.
    async with aclosing(graph.astream(input, config)) as stream:
        async for chunk in stream:
            if stop.is_set():
                print("interrupted!")
                break
            print(chunk)

    # The state as of the last completed step is still there:
    print("\nsaved state:", (await graph.aget_state(config)).next)


if __name__ == "__main__":
    asyncio.run(main())
