import os

from langchain.chains import GraphCypherQAChain
from langchain.prompts import PromptTemplate
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI

DRAGAN_QA_MODEL = os.getenv("DRAGAN_QA_MODEL")
DRAGAN_CYPHER_MODEL = os.getenv("DRAGAN_CYPHER_MODEL")

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

graph.refresh_schema()

cypher_generation_template = """
Task:
Generate Cypher query for a Neo4j graph database.

Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Schema:
{schema}

Note:
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything other than
for you to construct a Cypher statement. Do not include any text except
the generated Cypher statement. Make sure the direction of the relationship is
correct in your queries. Make sure you alias both entities and relationships
properly. Do not run any queries that would add to or delete from
the database. Make sure to alias all statements that follow as with
statement (e.g. WITH d as Drug, i as Disease, t as Target )
If you need to divide numbers, make sure to filter the denominator to be non zero.

# Examples:
# If the question is "What diseases are treated by the drug Intedanib?" 
MATCH (d:Drug)-[:TREATS]->(i:Disease)
WHERE d.name_drug = 'Intedanib' 
RETURN i.disease AS DiseaseName, i.icd AS ICDCode, i.clinicalstatus AS ClinicalStatus

# If the question is What kind of drugs affect cell wall formation?
MATCH (d:Drug)-[:INTERACTS]->(t:Target)
WHERE t.function_target =~ "(?i).*cell wall formation.*"
RETURN d.name_drug AS DrugName, d.id_drug AS DrugID, t.name_target AS TargetName, t.function_target AS TargetFunction

# If the question is what drugs affect vitamin k metabolism
MATCH (d:Drug)-[:INTERACTS]->(t:Target)
WHERE t.function_target =~ "(?i).*vitamin\\s?k\\s?metabolism.*"
RETURN d.name_drug AS DrugName, d.id_drug AS DrugID, t.name_target AS TargetName, t.function_target AS TargetFunction

Make sure to use IS NULL or IS NOT NULL when analyzing missing properties.
Never return embedding properties in your queries. You must never include the
statement "GROUP BY" in your query.

If you need to divide numbers, make sure to filter the denominator to be non
zero.

The question is:
{question}
"""

cypher_generation_prompt = PromptTemplate(
    input_variables=["schema", "question"], template=cypher_generation_template
)

qa_generation_template = """You are an assistant that takes the results
from a Neo4j Cypher query and forms a human-readable response. The
query results section contains the results of a Cypher query that was
generated based on a user's natural language question.

Query Results:
{context}

Question:
{question}

Instructions:
- If the query results are empty (e.g., []), respond with exactly:
  "There is no information associated with a specific drug in the database."
- If the query results are not empty, provide a detailed and complete response using all relevant results. Ensure lists or multiple results are formatted clearly.

Example Output for Empty Results:
"There is no information associated with a specific drug in the database."

Example Output for Non-Empty Results:
- Disease: Colorectal cancer (ICD: ICD-11: 2B91.Z, Status: Approved)
- Disease: Idiopathic pulmonary fibrosis (ICD: ICD-11: CB03.4, Status: Approved)

Always follow these instructions exactly and never add any extra context or explanation.
"""

qa_generation_prompt = PromptTemplate(
    input_variables=["context", "question"], template=qa_generation_template
)

dragan_cypher_chain = GraphCypherQAChain.from_llm(
    cypher_llm=ChatOpenAI(model=DRAGAN_CYPHER_MODEL, temperature=0),
    qa_llm=ChatOpenAI(model=DRAGAN_QA_MODEL, temperature=0),
    graph=graph,
    verbose=True,
    qa_prompt=qa_generation_prompt,
    cypher_prompt=cypher_generation_prompt,
    validate_cypher=True,
    top_k=100,
)
