'use strict'

const tracer = require('dd-trace').init(
  // { llmobs: { mlApp: 'test' } }
);
// const llmobs = tracer.llmobs;
tracer.use('express', false)
tracer.use('http', false)
tracer.use('dns', false)

const express = require('express');

const OpenAI = require('openai');
const client = new OpenAI();

const app = express();
app.use(express.json());

const spans = {};

const tracerVersion = require('dd-trace/package.json').version
app.get("/sdk/info", (req, res) => {
    res.json({ version: tracerVersion });
});

app.post('/openai/chat_completion', async (req, res) => {
  const { prompt } = req.body;
  await client.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [{ role: 'user', content: prompt }],
    max_tokens: 35
  });

  res.json({});
});

// app.post('/sdk/task', (req, res) => {
//   const { name, session_id, ml_app } = req.body;
//   const current = tracer.scope().active();
//   const span = tracer.startSpan(name, { childOf: current });

//   spans[span.context().toSpanId()] = span;

//   res.json({});
// })

app.listen(process.env.PORT, '0.0.0.0', () => {
  console.log('Server listening on port ' + process.env.PORT);
})