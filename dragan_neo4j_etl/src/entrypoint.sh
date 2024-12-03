#!/bin/bash

# Run any setup steps or pre-processing tasks here
echo "Running ETL to move DRAGAN data from .csv files to Neo4j..."

# Run the ETL script
python dragan_bulk_csv_write.py