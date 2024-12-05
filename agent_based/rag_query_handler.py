import agent_based.agent.task_splitter as task_splitter
from agent_based.agent import agent_coordinator, geospatial_agent, final_answer_generator

INSTRUCTION = """
    """


# Main function
def do_ask(question):
    split_questions, split_prompt = task_splitter.inquire(question)

    print(split_questions)

    history = []
    history.append(f"First prompt: {question}")

    for q in split_questions:
        history.append(f"Split question: {q}")
        agent_questions, agent_prompt = agent_coordinator.inquire(q)

        if "USER" in agent_questions:
            print(agent_questions["USER"])
            user_input = input("Please provide additional information: ")

            history.append(f"USER_AGENT: {agent_questions['USER']} | RESPONSE: {user_input}")

        if "GEOSPATIAL" in agent_questions:
            print(agent_questions["GEOSPATIAL"])

            geo_result, geo_prompt = geospatial_agent.inquire(agent_questions["GEOSPATIAL"])
            history.append(f"GEOSPATIAL: {agent_questions['GEOSPATIAL']} | RESPONSE: {geo_result}")

        if "REGULATION" in agent_questions:
            print(agent_questions["REGULATION"])
            print("[REGULATION] not implemented yet")

    print(history)

    final_answer = final_answer_generator.inquire(history)
    print(f"Final answer: {final_answer}")


if __name__ == "__main__":
    question = "관정도서관 위치가 어디야 거기 근처 식당 위치도 알고싶어."
    do_ask(question)
    # questions, full_prompt =
    # print(questions)
