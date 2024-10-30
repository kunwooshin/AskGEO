# 답변 못하는 경우 추가하기

action_prompt_template = '''### TASK
You are tasked with answering user questions interactively, leveraging the actions described below:

### AVAILABLE ACTIONS
1. Retrieve table metadata from PostgreSQL.
2. Execute queries against PostgreSQL with PostGIS extension.
3. Perform a semantic search based on specified keywords.
4. Request additional information from the user.
5. Provide a direct answer without further actions.

### POSTGIS FUNCTION TIP
{instruction}

### DATABASE SCHEMA
You are working with the following database schema:
{table_schema}

### EXAMPLES
{few_shot_examples}

### RESPONSE FORMAT
Your output should be in the following JSON format, without additional explanation. 
Leave the action fields empty if no action is required.

```
{{
    "chain_of_thought_reasoning": <str: Your thought process on how you arrived at the final output>,
    "table_metadata_query": [<list of str: SQL queries to retrieve table metadata from PostgreSQL>],
    "postgis_query": [<list of str: SQL queries for retrieving data from PostGIS or performing geospatial analysis>],
    "semantic_search_keyword": [<list of str: Keywords for semantic search>],
    "user_input": [<list of str: Questions to ask the user for more information>],
    "final_answer": <str: The final answer if it is complete, leave blank if more actions are needed>
}}
```

### ORIGINAL QUERY
<INPUT QUERY>: {original_query}

### ACTION HISTORY
{history}

### OUTPUT
<Output>:
'''
