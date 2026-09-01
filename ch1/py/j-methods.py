from langchain_openai.chat_models import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1-mini")

completion = model.invoke("Hi there!")
# Hi!

completions = model.batch(["Hi there!", "Bye!"])
# ['Hi!', 'See you!']

for token in model.stream("Bye!"):
    print(token)
    # Good
    # bye
    # !
