import os

from openai import OpenAI

# Initialize OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_key=OPENAI_API_KEY)

INSTRUCTION = """
You are a knowledgeable assistant tasked with generating a final answer based on a series of questions and their corresponding responses. Use the provided information to create a clear, coherent, and comprehensive answer.

Here is the data you have:

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
def inquire(history):
    # Example user question
    iteration = 0

    # Create initial prompt
    prompt = INSTRUCTION

    for line in history:
        prompt += line + "\n"

    response = generate_response(prompt)

    return response, prompt


if __name__ == "__main__":
    question = "공대위치와 도서관위치를 알려줘."
    result, full_prompt = inquire(question)
    print(result)
