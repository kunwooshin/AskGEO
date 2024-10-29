import askgeo.database.geodb.postgres as geodb
import askgeo.database.vecdb.chroma as vecdb
import askgeo.llm.gpt as llm
from askgeo.dto.dto import *
from askgeo.util.util import log


def setup():
    pass  # 필요한 셋업 수행


def start_chat(user_prompt):
    log('rag', 'user_prompt', user_prompt)

    # 첫 프롬프트에 필요한 정보 수집
    table_schema = ''
    table_names = vecdb.retrieve_table_names(user_prompt)
    table_schema = geodb.retrieve_table_metadata(table_names)

    # 첫 프롬프트 수행
    first_prompt = FirstPrompt(original_query=user_prompt,
                               instruction='single coordinate (latitude, longitude) should be wrapped with ST_AsText(ST_MakePoint())',
                               table_schema=table_schema,
                               few_shot_examples='')

    conversation = Conversation(first_prompt=first_prompt)

    interaction = llm.inquire_first_prompt(first_prompt)

    # 이후 action에 따라 대화 수행
    while True:
        conversation.add_interaction(interaction)

        retrieve_action = interaction.retrieve_action

        if retrieve_action.is_complete():
            break

        for retrieval in retrieve_action.metadata:
            query = retrieval.query
            response = vecdb.retrieve_metadata(query)
            retrieval.response = response

        for retrieval in retrieve_action.geospatial:
            query = retrieval.query
            response = geodb.execute_sql(query)
            retrieval.response = response

        for retrieval in retrieve_action.semantic:
            query = retrieval.query
            response = vecdb.retrieve_semantic(query)
            retrieval.response = response

        for retrieval in retrieve_action.user:
            query = retrieval.query
            response = input(query + "\nPlease type your response: ")
            retrieval.response = response

        log('rag', 'retrieve_action', retrieve_action)

        interaction = llm.inquire_action(first_prompt, conversation)

    return conversation.get_final_answer()
