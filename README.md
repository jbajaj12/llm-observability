# LLM Observability Jupyter Notebooks

These notebooks introduce you to Datadog's [LLM Observability Python SDK](https://docs.datadoghq.com/tracing/llm_observability/sdk/) using hands-on examples.

For a detailed instrumentation guide, see [Trace an LLM Application](https://docs.datadoghq.com/tracing/llm_observability/trace_an_llm_application/).

## Prerequisites

- [A Datadog API key](https://docs.datadoghq.com/account_management/api-app-keys)
- [An OpenAI API key](https://platform.openai.com/docs/quickstart/account-setup)

## Setup

- Note: if [your Datadog site](https://docs.datadoghq.com/getting_started/site/#access-the-datadog-site) (`DD_SITE`) is not provided, the value defaults to `"datadoghq.com"`
- Feel free to update the `DD_LLMOBS_ML_APP` variable to any custom app name.
- `DD_LLMOBS_AGENTLESS_ENABLED=1` is only required if the Datadog Agent is not running. If the agent is running in your production environment, make sure this environment variable is unset.

#### Launch Jupyter notebooks

Go to localhost:8888

## Notebooks

### 1. Tracing a simple LLM call

**[This notebook](./1-llm-span.ipynb)** shows you how to create and trace a simple LLM call.

<img src="./images/llm-span.png" height="350" >

### 2. Tracing an LLM Workflow

**[This notebook](./2-workflow-span.ipynb)** shows you how to create and trace a more complex, static series of steps that involves a tool call in addition to a call to an LLM.

<img src="./images/workflow-span.png" height="350" >

### 3. Tracing an LLM Agent

**[This notebook](./3-agent-span.ipynb)** shows you how to create and trace an LLM powered agent that calls tools and makes decisions based on data about what to do next.

<img src="./images/agent-span.png" height="350" >

### 4. Tracing and evaluating a RAG workflow

**[This notebook](./4-custom-evaluations.ipynb)** shows you how to create, trace, and evaluate a RAG workflow.

<img src="./images/rag-span.png" height="350" >

## Teardown

When you're done with the tutorials:

```docker compose down
```



## Commands Used:

