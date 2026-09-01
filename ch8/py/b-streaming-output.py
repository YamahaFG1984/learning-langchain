"""Intermediate output: stream the update produced by each node."""

from langchain_core.messages import HumanMessage

from agent import QUESTION, build_graph

graph = build_graph()

input = {"messages": [HumanMessage(QUESTION)]}

# stream_mode="updates" yields {node_name: state_update} as soon as a node finishes.
# Other options: "values" (the whole state), "messages" (token-by-token), "debug".
for c in graph.stream(input, stream_mode="updates"):
    print(c)

print("\n--- token-by-token streaming ---\n")

# `stream_mode="messages"` yields (chunk, metadata) for every LLM token produced
# anywhere inside the graph.
for chunk, metadata in graph.stream(input, stream_mode="messages"):
    if chunk.content:
        print(chunk.content, end="", flush=True)
print()
