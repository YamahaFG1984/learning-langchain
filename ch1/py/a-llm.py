from langchain_openai.chat_models import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1-mini")

response = model.invoke("The sky is")
print(response.content)
