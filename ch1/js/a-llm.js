import { ChatOpenAI } from '@langchain/openai';

const model = new ChatOpenAI({ model: 'gpt-4.1-mini' });

const response = await model.invoke('The sky is');
console.log(response);
