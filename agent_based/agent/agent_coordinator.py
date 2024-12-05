import json
import os

from dotenv import load_dotenv
from openai import OpenAI

# Initialize OpenAI
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_key=OPENAI_API_KEY)

INSTRUCTION = """
You are an agent coordinator for a Retrieval-Augmented Generation (RAG) system. Your task is to:
1. Analyze the user query which is bounded to Seoul National University.
2. Determine which agents should be used to answer the query. Use as less as possible.
   - USER: Collect additional information from the user.
   - GEOSPATIAL: Run query to postgis database with OSM database.
   - REGULATION: Run query to chroma database with chunked regulation data.
3. Create specific prompt for each chosen agent.

Provide the output as a Python dictionary, where:
- The key is the agent name ("USER", "GEOSPATIAL", "REGULATION").
- The value is a question.

For example:
Input: "What are the zoning regulations for building a hospital in downtown Berlin?"
Output: {
    "USER": "Do you need zoning regulations for a specific district or the entire downtown area?",
    "GEOSPATIAL": "Get geographical boundaries of downtown Berlin in OSM data.",
    "REGULATION": "Get the zoning regulations for hospitals in Berlin according to the regulations database."
}

Now, analyze the following query and generate agent-specific questions in the exact format without any additional information:
"""


# cot 넣어야할까?

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
    response_str = response_str.replace("```python", '').replace("```", '');
    print(response_str)
    response = json.loads(response_str)

    return response, prompt


if __name__ == "__main__":
    question = "공대의 정확한 위치는 어디인가요?"
    result, full_prompt = inquire(question)
    print(result)
