# Function to get response from OpenAI LLM
import os

from dotenv import load_dotenv
from openai import OpenAI

from askgeo.util.util import log

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = None


def get_llm():
    global llm
    if llm is None:
        llm = OpenAI(api_key=OPENAI_API_KEY)
    return llm


def inquire_prompt(prompt):
    log("gpt", "prompt", prompt)

    response = get_llm().chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )
    content = response.choices[0].message.content
    log("gpt", "response", content)

    return content
