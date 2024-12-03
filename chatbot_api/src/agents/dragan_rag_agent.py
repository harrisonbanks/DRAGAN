import os

from ..chains.dragan_cypher_chain import dragan_cypher_chain
from ..chains.dragan_textanalysis_chain import textanalysis_vector_chain
from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain_openai import ChatOpenAI

DRAGAN_AGENT_MODEL = os.getenv("DRAGAN_AGENT_MODEL")

dragan_agent_prompt = hub.pull("hwchase17/openai-functions-agent")

tools = [
    Tool(
        name="TextAnalysis",
        func=textanalysis_vector_chain.invoke,
        description="""Useful when you need to answer questions
        about drugs, disease, targets, or any other qualitative
        question that could be answered about drugs and their treatment of 
        disease using semantic search. 
        Not useful for answering objective questions that involve
        counting, percentages, aggregations, or listing facts. Use the
        entire prompt as input to the tool. For instance, if the prompt is
        "What kind of drugs affect cell wall formation?", the input should be
        "What kind of drugs affect cell wall formation?".
        """,
    ),
    Tool(
        name="Graph",
        func=dragan_cypher_chain.invoke,
        description="""Useful for answering questions about drugs,
        diseases, targets. Use the entire prompt as
        input to the tool. For instance, if the prompt 
        is "what diseases are treated by the drug named Intedanib?", the input should 
        be "what diseases are treated by the drug named Intedanib?".
        """
    ),
]

chat_model = ChatOpenAI(
    model=DRAGAN_AGENT_MODEL,
    temperature=0,
)

dragan_rag_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=dragan_agent_prompt,
    tools=tools,
)

dragan_rag_agent_executor = AgentExecutor(
    agent=dragan_rag_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
)
