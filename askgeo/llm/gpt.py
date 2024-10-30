# Function to get response from OpenAI LLM
import os

from dotenv import load_dotenv
from openai import OpenAI

from askgeo.dto.dto import *
from askgeo.llm import const
from askgeo.util.util import log

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

conn = None


def get_llm():
    global conn
    if conn is None:
        conn = OpenAI(api_key=OPENAI_API_KEY)
    return conn


def generate_gpt_response(prompt):
    log("gpt", "chat", prompt)
    response = get_llm().chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )
    content = response.choices[0].message.content
    log("gpt", "chat-response", content)
    return content


def inquire_prompt(prompt):
    log("gpt", "prompt", prompt)

    response = generate_gpt_response(prompt)
    log("gpt", "response", response)

    return response


def to_interaction(prompt, response):
    retrieve_action = RetrieveAction.from_json(response)
    return Interaction(prompt, response, retrieve_action)


def inquire_first_prompt(fist_prompt: FirstPrompt):
    prompt = const.action_prompt_template.format(instruction=fist_prompt.instruction,
                                                 table_schema=fist_prompt.table_schema,
                                                 few_shot_examples=fist_prompt.few_shot_examples,
                                                 original_query=fist_prompt.original_query,
                                                 history="")
    response = generate_gpt_response(prompt)
    interaction = to_interaction(prompt, response)
    return interaction


def inquire_action(fist_prompt: FirstPrompt, conversation: Conversation):
    history = conversation.action_history()
    prompt = const.action_prompt_template.format(instruction=fist_prompt.instruction,
                                                 table_schema=fist_prompt.table_schema,
                                                 few_shot_examples=fist_prompt.few_shot_examples,
                                                 original_query=fist_prompt.original_query,
                                                 history=history)
    response = generate_gpt_response(prompt)
    interaction = to_interaction(prompt, response)
    return interaction
