/**
 * Supervisor multi-agent architecture (Chapter 7).
 *
 * A supervisor node uses structured output to decide which worker agent runs
 * next, or whether the work is FINISHed.
 */
import { ChatOpenAI } from '@langchain/openai';
import {
  StateGraph,
  Annotation,
  MessagesAnnotation,
  START,
  END,
} from '@langchain/langgraph';
import { z } from 'zod';

// The workers the supervisor can delegate to. Give them self-explanatory names:
// the LLM only ever sees the names.
const agents = ['researcher', 'coder'];

const SupervisorDecision = z.object({
  next: z
    .enum(['researcher', 'coder', 'FINISH'])
    .describe('Who should act next, or FINISH when the task is done.'),
});

const model = new ChatOpenAI({ model: 'gpt-4.1', temperature: 0 });
const supervisorModel = model.withStructuredOutput(SupervisorDecision);

const systemPromptPart1 = `You are a supervisor tasked with managing a conversation between the following workers: ${agents.join(
  ', '
)}. Given the following user request, respond with the worker to act next. Each worker will perform a task and respond with their results and status. When finished, respond with FINISH.`;

const systemPromptPart2 = `Given the conversation above, who should act next? Or should we FINISH? Select one of: ${agents.join(
  ', '
)}, FINISH`;

// Shared state: the message history plus the supervisor's routing decision.
const StateAnnotation = Annotation.Root({
  ...MessagesAnnotation.spec,
  next: Annotation(),
});

const supervisor = async (state) => {
  const decision = await supervisorModel.invoke([
    { role: 'system', content: systemPromptPart1 },
    ...state.messages,
    { role: 'system', content: systemPromptPart2 },
  ]);
  // A node must return a state update, so wrap the decision in the `next` key.
  return { next: decision.next };
};

const researcher = async (state) => {
  const response = await model.invoke([
    {
      role: 'system',
      content:
        'You are a research assistant. Analyze the request and provide relevant information. Be concise.',
    },
    ...state.messages,
  ]);
  return { messages: [response] };
};

const coder = async (state) => {
  const response = await model.invoke([
    {
      role: 'system',
      content:
        'You are a coding assistant. Implement the requested functionality. Be concise.',
    },
    ...state.messages,
  ]);
  return { messages: [response] };
};

const graph = new StateGraph(StateAnnotation)
  .addNode('supervisor', supervisor)
  .addNode('researcher', researcher)
  .addNode('coder', coder)
  .addEdge(START, 'supervisor')
  // Route to one of the agents, or exit, based on the supervisor's decision.
  .addConditionalEdges(
    'supervisor',
    (state) => (state.next === 'FINISH' ? END : state.next),
    ['researcher', 'coder', END]
  )
  .addEdge('researcher', 'supervisor')
  .addEdge('coder', 'supervisor')
  .compile();

// Example usage
const initialState = {
  messages: [
    {
      role: 'user',
      content: 'I need help analyzing some data and creating a visualization.',
    },
  ],
};

for await (const step of await graph.stream(initialState)) {
  for (const [node, update] of Object.entries(step)) {
    console.log(`\n--- ${node} ---`);
    if (update.next) console.log('next:', update.next);
    if (update.messages?.length) {
      console.log(`${String(update.messages.at(-1).content).slice(0, 200)}...`);
    }
  }
}
