schema_retrieval_query = '''
SELECT
    column_name,
    data_type,
    is_nullable
FROM
    INFORMATION_SCHEMA.COLUMNS
WHERE
    table_name = :table_name
'''

text_to_sql_prompt = '''### TASK
You are tasked with generating a SQL query according to a input user request.

You will be provided an input NL query (and potentially a hint)

### TIP: PostGIS geospatial function
{instruction}

### SCHEMA
You are working with the following schema:
{table_schema}

### EXAMPLES
{few_shot_examples}

### FORMATTING
Your output should be of the following JSON format with no explanation:
{{
    "chain_of_thought_reasoning": <str: Your thought process on how you arrived at the full SQL query.>,
    "full_sql_query": <str: the full SQL query>
}}

### OUTPUT
<INPUT QUERY>: {user_query}
<Output>: 
'''
