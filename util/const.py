input_prompt = '''You are an assistant that converts natural language geospatial queries into structured JSON. The JSON should include the following fields:

1. "action": The operation or function to perform (e.g., "find_nearby_buildings_by_polygon").
2. "parameters": A dictionary containing the parameters required for the action. For example:
   - "building_name": The name of the building or location specified in the query.
   - "distance": The distance in meters if the query specifies a proximity range.

Always ensure the JSON is valid and corresponds directly to the intent of the user's query. Do not change the type of parameters in example. If the user's query is ambiguous or does not match a supported action, include an "error" field explaining the issue.

### Examples:

#### Example 1:
**User Query**: "Find all buildings within 200 meters of the Administration Building."
**Parsed Query**:
{{
  "action": "find_nearby_buildings",
  "parameters": {{
    "building_name": "Administration Building",
    "distance": 200
  }}
}}

#### Example 2:
**User Query**: "What is the coordinate of the Administration Building.?"
**Parsed Query**:
{{
  "action": "find_coordinates",
  "parameters": {{
    "building_name": "Administration Building",
  }}
}}

#### Example 3:
**User Query**: "I want a list of all buildings inside Seoul National University."
**Parsed Query**:
{{
  "action": "list_all_buildings",
  "parameters": {{
    "location": "Seoul National University"
  }}
}}

#### Example 4 (Ambiguous Query):
**User Query**: "Tell me something about Seoul National University."
**Parsed Query**:
{{
  "action": "ambiguous_query",
  "parameters": {{}}
}}

Now, parse the following user query into a structured JSON format:
**User Query**: "{user_query}"
'''

nearby_query = """
SELECT 
    target.*,
    ST_Distance(
        target.geometry::geography,
        (SELECT geometry::geography
         FROM snu
         WHERE name = :building_name)
    ) AS distance
FROM snu AS target
WHERE ST_DWithin(
    target.geometry::geography,
    (SELECT geometry::geography
     FROM snu
     WHERE name = :building_name),
    :distance
)
AND target.name != 'Seoul National University Gwanak Campus'
ORDER BY distance;
"""

exact_query = """
SELECT *
FROM snu
WHERE snu.name = :building_name
"""

closest_query = """
SELECT *
FROM snu AS target
WHERE snu.name = :building_name
"""

total_area_query = """
SELECT *
FROM snu AS target
WHERE snu.name = :building_name
"""
