import json
from dataclasses import dataclass, field
from typing import List


@dataclass
class FirstPrompt:
    original_query: str
    instruction: str
    table_schema: str
    few_shot_examples: str


@dataclass
class Retrieval:
    query: str
    response: str = ''

    def __str__(self):
        return f'{self.query}\n{self.response}'


@dataclass
class RetrieveAction:
    chain_of_thought_reasoning: str = ''
    metadata: List[Retrieval] = field(default_factory=list)
    geospatial: List[Retrieval] = field(default_factory=list)
    semantic: List[Retrieval] = field(default_factory=list)
    user: List[Retrieval] = field(default_factory=list)
    final_answer: str = ''

    @staticmethod
    def from_json(json_str: str) -> 'RetrieveAction':
        data = json.loads(json_str)

        def create_retrieval_list(queries: List[str]) -> List[Retrieval]:
            return [Retrieval(query=q) for q in queries]

        return RetrieveAction(
            chain_of_thought_reasoning=data.get("chain_of_thought_reasoning", ''),
            metadata=create_retrieval_list(data.get("table_metadata_query", [])),
            geospatial=create_retrieval_list(data.get("postgis_query", [])),
            semantic=create_retrieval_list(data.get("semantic_search_keyword", [])),
            user=create_retrieval_list(data.get("user_input", [])),
            final_answer=data.get("final_answer", '')
        )

    def add_metadata(self, query: str, response: str):
        self.metadata.append(Retrieval(query, response))

    def add_geospatial(self, query: str, response: str):
        self.geospatial.append(Retrieval(query, response))

    def add_semantic(self, query: str, response: str):
        self.semantic.append(Retrieval(query, response))

    def add_user(self, query: str, response: str):
        self.user.append(Retrieval(query, response))

    def __str__(self):
        return '\n'.join(
            [
                f'Metadata:\n{str(self.metadata)}',
                f'Geospatial:\n{str(self.geospatial)}',
                f'Semantic:\n{str(self.semantic)}',
                f'User:\n{str(self.user)}'
            ]
        )

    def is_complete(self):
        return self.final_answer != ''


@dataclass
class Interaction:
    prompt: str
    response: str
    retrieve_action: RetrieveAction

    def action_history(self):
        return self.retrieve_action


@dataclass
class Conversation:
    first_prompt: FirstPrompt
    interactions: List[Interaction] = field(default_factory=list)

    def add_interaction(self, interaction: Interaction):
        self.interactions.append(interaction)

    def action_history(self):
        return '\n'.join([f'{interaction.action_history()}' for interaction in self.interactions])

    def get_final_answer(self):
        return self.interactions[-1].retrieve_action.final_answer
