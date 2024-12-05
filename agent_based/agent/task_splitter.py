import os
import json

from dotenv import load_dotenv
from openai import OpenAI

# Initialize OpenAI
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_key=OPENAI_API_KEY)

INSTRUCTION = """
You are a task-splitting assistant. Your job is to break a complex user query into multiple specific and actionable questions bounded in Seoul National University.
The goal is to ensure each question focuses on one clear aspect of the original query.
The answer from a previous question can be used in the next steps.

You have access to the following types of data:
1. **OSM data** (OpenStreetMap data), which provides geographical and spatial information.
2. **Regulation data**, which provides legal and policy-related information.

Provide the output as a Python list of strings. For example:
Input: "Tell me about urban planning strategies in Europe and their legal frameworks."
Output: [
    "What are the key urban planning strategies in Europe?",
    "What are the legal frameworks that govern urban planning in Europe?"
]

Now, split the following query into multiple specific questions and provide the output in the same format:
"""


# Function to refine the GPT query
def generate_response(prompt):
    response = llm.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# Main function
def inquire(question):
    # Example user question
    iteration = 0

    # Create initial prompt
    prompt = INSTRUCTION + "\nQuestion: " + question
    print(f"[task_splitter] User Question: {question}")
    response_str = generate_response(prompt)
    response_str = response_str.replace("```python",  '').replace("```", '');
    print(response_str)
    response = json.loads(response_str)

    return response, prompt


if __name__ == "__main__":
    question = "공대위치와 도서관위치를 알려줘."
    result, full_prompt = inquire(question)
    print(result)
