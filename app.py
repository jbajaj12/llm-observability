# app.py
from dotenv import load_dotenv
load_dotenv()

from ddtrace.llmobs import LLMObs
LLMObs.enable()

from openai import OpenAI
import json
import os

oai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

sys_prompt = """
Your task is to 
1. Summarize the given text at a 6th grade reading level in no more than 2 sentences.
2. Identify what topics the text belongs to that would allow you to categorize it in a school library.
Format your output strictly following this JSON convention:
{	
    "topics": <[insert array of topics here]>,
    "summary": <insert summary here>
}
"""

def summarize(text, prompt=sys_prompt):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text},
    ]
    # llm span auto-instrumented via our openai integration
    response_content = (
        oai_client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
        )
        .choices[0]
        .message.content
    )
    return json.loads(response_content)
