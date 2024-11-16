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
statement (e.g. WITH d as Drug, i as Disease, t as Target, t.name_target as name_target, d.name_drug as name_drug, i.disease as disease )
If you need to divide numbers, make sure to
filter the denominator to be non zero.

Examples:
# What diseases are treated by the drug Intedanib?
MATCH (d:Drug {name_drug: "Intedanib"})-[:TREATS]->(disease:Disease)
RETURN disease.disease AS DiseaseName, disease.icd AS ICDCode, disease.clinicalstatus AS ClinicalStatus

# What kind of drugs affect cell wall formation?
MATCH (d:Drug)-[:INTERACTS]->(t:Target)
WHERE t.function_target =~ "(?i).*cell wall formation.*"
RETURN d.name_drug AS DrugName, d.id_drug AS DrugID, t.name_target AS TargetName, t.function_target AS TargetFunction

# what drugs affect vitamin k metabolism
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
generated based on a users natural language question. The provided
information is authoritative, you must never doubt it or try to use
your internal knowledge to correct it. Make the answer sound like a
response to the question.

Query Results:
{context}

Question:
{question}

If the provided information is empty, say you don't know the answer.
Empty information looks like this: []

If the information is not empty, you must provide an answer using the
results. If the question involves a time duration, assume the query
results are in units of days unless otherwise specified.

When names are provided in the query results, such as drug names,
beware  of any names that have commas or other punctuation in them.
For instance, '6,7-dimethoxy-4-(3-phenoxyprop-1-ynyl)quinazoline' is a single drug name,
not multiple drugs. Make sure you return any list of names in
a way that isn't ambiguous and allows someone to tell what the full drug
names are.

Never say you don't have the right information if there is data in
the query results. Make sure to show all the relevant query results
if you're asked.

Helpful Answer:
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
