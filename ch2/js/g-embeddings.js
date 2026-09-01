import { OpenAIEmbeddings } from '@langchain/openai';

const model = new OpenAIEmbeddings({ model: 'text-embedding-3-small' });
const embeddings = await model.embedDocuments([
  'Hi there!',
  'Oh, hello!',
  "What's your name?",
  'My friends call me World',
  'Hello World!',
]);

console.log(embeddings);
