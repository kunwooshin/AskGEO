sample_data = {'create_table_query': '''
DROP TABLE IF EXISTS citibike_stations;

CREATE TABLE citibike_stations (
    station_id VARCHAR NOT NULL,
    name VARCHAR,
    short_name VARCHAR,
    latitude FLOAT,
    longitude FLOAT,
    region_id BIGINT,
    rental_methods VARCHAR,
    capacity BIGINT,
    eightd_has_key_dispenser BOOLEAN,
    num_bikes_available BIGINT,
    num_bikes_disabled BIGINT,
    num_docks_available BIGINT,
    num_docks_disabled BIGINT,
    is_installed BOOLEAN,
    is_renting BOOLEAN,
    is_returning BOOLEAN,
    eightd_has_available_keys BOOLEAN,
    last_reported TIMESTAMP
);
''' ,
'insert_query' : '''
INSERT INTO citibike_stations (
    station_id, name, short_name, latitude, longitude, region_id, rental_methods, 
    capacity, eightd_has_key_dispenser, num_bikes_available, num_bikes_disabled, 
    num_docks_available, num_docks_disabled, is_installed, is_renting, 
    is_returning, eightd_has_available_keys, last_reported
) VALUES (
    :station_id, :name, :short_name, :latitude, :longitude, :region_id, :rental_methods, 
    :capacity, :eightd_has_key_dispenser, :num_bikes_available, :num_bikes_disabled, 
    :num_docks_available, :num_docks_disabled, :is_installed, :is_renting, 
    :is_returning, :eightd_has_available_keys, :last_reported
);
'''}

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