#
# DRAGAN text analysis chain
# Target Function text analysis
# test script: 
# import dotenv
# dotenv.load_dotenv()
# from chatbot_api.src.chains.dragan_textanalysis_chain import ( textanalysis_vector_chain )
# query = """give me an example of a target function and what is its target""" 
# response = textanalysis_vector_chain.invoke(query)
# response.get("result")
#

import os

from langchain.chains import RetrievalQA
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

DRAGAN_QA_MODEL = os.getenv("DRAGAN_QA_MODEL")

neo4j_vector_index = Neo4jVector.from_existing_graph(
    embedding=OpenAIEmbeddings(),
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="targetdata",
    node_label="Target",
    text_node_properties=[
        "id_target",
        "id_unipro",
        "name_target",
        "name_gene",
        "type_target",
        "function_target"
    ],
    embedding_node_property="embedding",
)


# TEST 1: full context provided
textanalysis_template = """Your job is to query the target function dataset to answer questions about specific biological target functions and their roles. Use the following context to interpret and respond to questions accurately. Be as detailed as possible, but don't make up any information that's not from the dataset. If you don't know an answer, say you don't know.
For Target Identification Queries, focus on identifying targets based on general biological roles or processes. For example, if a user asks for targets involved in "cell proliferation," look for related terms in the function_target field that mention cell growth or differentiation.
For Function-Based Queries, retrieve targets based on specified biological or molecular functions, such as "DNA repair" or "cell cycle regulation," by filtering the function_target field for matching terms.
For Pathway Interaction Queries, look for targets associated with specific cellular pathways or signaling cascades, like "MAP kinase" or "AKT signaling." Check the function_target descriptions to find relevant pathway interactions.
For Gene and Protein-Specific Queries, respond to requests for detailed information on specific genes or proteins. Match gene names or terms in the name_gene or name_target fields to provide all available details on the target.
For Target Type and Success Status Queries, filter targets by type or success status. For queries about "successful targets" or specific types, use the type_target and status fields to provide relevant entries.
If a question does not match any of these categories or lacks sufficient data in the context, let the user know you don’t have an answer. 
{context}
"""

# # TEST 2: limited bioengineering and drug context
# textanalysis_template = """Your job is to query the target function dataset to answer questions about specific biological target functions and their roles. Use the following context to interpret and respond to questions accurately. Be as detailed as possible, but don't make up any information that's not from the dataset. If you don't know an answer, say you don't know.
# For Target Identification Queries, focus on identifying targets based on general biological roles or processes. For example, if a user asks for targets involved in "cell proliferation," look for related terms in the function_target field that mention cell growth or differentiation.
# For Function-Based Queries, retrieve targets based on specified biological or molecular functions, such as "DNA repair" or "cell cycle regulation," by filtering the function_target field for matching terms.
# {context}
# """

# TEST 3: basic instructions on target functions and roles
# textanalysis_template = """Your job is to query the target function dataset to answer questions about specific biological target functions and their roles. Use the following context to interpret and respond to questions accurately. Be as detailed as possible, but don't make up any information that's not from the dataset. If you don't know an answer, say you don't know.
# """

textanalysis_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"], template=textanalysis_template
    )
)

textanalysis_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [textanalysis_system_prompt, textanalysis_human_prompt]

textanalysis_prompt = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

textanalysis_vector_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model=DRAGAN_QA_MODEL, temperature=0),
    chain_type="stuff",
    retriever=neo4j_vector_index.as_retriever(k=12),
)

textanalysis_vector_chain.combine_documents_chain.llm_chain.prompt=textanalysis_prompt