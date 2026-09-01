import { z } from "zod";
import { ChatOpenAI } from "@langchain/openai";

const joke = z.object({
  setup: z.string().describe("The setup of the joke"),
  punchline: z.string().describe("The punchline to the joke"),
});

let model = new ChatOpenAI({
  model: "gpt-4.1-mini",
  temperature: 0,
});

model = model.withStructuredOutput(joke);

const result = await model.invoke("Tell me a joke about cats");
console.log(result);
