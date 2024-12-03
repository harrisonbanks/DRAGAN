#
# dragan_bulk_csv_write.py : load data to cloud AuraDB using github raw datafiles 
# TO RUN:   run docker desktop
#           cd /dragan_neo4j_etl
#           docker-compose up --build 

import logging
import os

from neo4j import GraphDatabase
from retry import retry

DRUGS_CSV_PATH = os.getenv("DRUGS_CSV_PATH")
TARGETS_CSV_PATH = os.getenv("TARGETS_CSV_PATH")
DISEASE_CSV_PATH = os.getenv("DISEASE_CSV_PATH")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

LOGGER = logging.getLogger(__name__)

NODES = ["Drug", "Target", "Disease"]

def _set_uniqueness_constraints(tx, node):
    query = f"""CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node})
        REQUIRE n.id IS UNIQUE;"""
    _ = tx.run(query, {})

@retry(tries=100, delay=10)
def load_dragan_graph_from_csv() -> None:
    """Load Dragan CSV Drug, Target and Disease data (nodes and properties) into Neo4j AuraDB"""

    driver = GraphDatabase.driver(
        NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )

    LOGGER.info("Setting uniqueness constraints on nodes")
    with driver.session(database="neo4j") as session:
        for node in NODES:
            session.execute_write(_set_uniqueness_constraints, node)

    LOGGER.info("Loading Drug nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{DRUGS_CSV_PATH}' AS drugdata
        MERGE (d:Drug {{   name_drug: drugdata.name_drug,
                            id: toInteger(drugdata.id),
                            id_target: drugdata.id_target,
                            id_drug: drugdata.id_drug,
                            clinicalstatus: drugdata.clinicalstatus}});
        """
        _ = session.run(query, {})

    LOGGER.info("Loading Disease nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{DISEASE_CSV_PATH}' AS diseasedata
        MERGE (i:Disease {{ disease: diseasedata.disease,
                            id: toInteger(diseasedata.id),
                            name_drug: diseasedata.name_drug,
                            id_drug: diseasedata.id_drug,
                            icd: diseasedata.icd,
                            clinicalstatus: diseasedata.clinicalstatus}});
        """
        _ = session.run(query, {})

    LOGGER.info("Loading Target nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{TARGETS_CSV_PATH}' AS targetdata
        MERGE (t:Target {{  id: toInteger(targetdata.id),
                            id_target: targetdata.id_target,
                            id_unipro: targetdata.id_unipro,
                            name_target: targetdata.name_target,
                            name_gene: targetdata.name_gene,
                            type_target: targetdata.type_target,
                            function_target: targetdata.function_target}});
        """
        _ = session.run(query, {})

    # Drug (d) -> TREATS -> Disease (i)
    LOGGER.info("Setting 'TREATS' relationships in Database")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{DISEASE_CSV_PATH}' AS diseasedata
            MATCH (d:Drug {{id_drug: diseasedata.id_drug}})
            MATCH (i:Disease {{disease: diseasedata.disease, id_drug: diseasedata.id_drug}})
            MERGE (d)-[:TREATS]->(i)
        """
        _ = session.run(query, {})

    # Drug (d) -> INTERACTS -> Target (t)
    LOGGER.info("Setting 'INTERACTS' relationships in Database")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{DRUGS_CSV_PATH}' AS drugdata
            MATCH (d:Drug {{id_drug: drugdata.id_drug}})
            MATCH (t:Target {{id_target: drugdata.id_target}})
            MERGE (d)-[:INTERACTS]->(t)
        """
        _ = session.run(query, {})

if __name__ == "__main__":
    load_dragan_graph_from_csv()
