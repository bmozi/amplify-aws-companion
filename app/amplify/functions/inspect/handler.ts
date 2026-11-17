export const handler = async (event: { arguments: { text: string } }) => {
  const text = event.arguments.text.trim();
  if (text.length > 10000) throw new Error('Use 10,000 characters or fewer.');
  return JSON.stringify({ words: text ? text.split(/\s+/).length : 0, characters: text.length, processedAt: new Date().toISOString(), service: 'AWS Lambda', note: 'Deterministic text inspection; no AI model is called.' });
};
