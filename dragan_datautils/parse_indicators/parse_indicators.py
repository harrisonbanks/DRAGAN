# parse_indicators: extract indicators from TTD target text file
# output .csv formatted: id,id_drug,name_drug,indication,disease,icd

import re

def parse_srcdata(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:  # Specify encoding
        data = f.read()

    # Split data by blank lines
    records = data.strip().split("\n\n")

    # Initialize an id counter starting at 0
    id_counter = 1

    # Open output file
    with open(output_file, 'w', encoding='utf-8') as out_f:  # Specify encoding
        # Write the header
        out_f.write("id,id_drug,name_drug,indication,disease,icd\n")
        
        # Process each record
        for record in records:
            lines = record.strip().splitlines()
            
            # Initialize variables for each record
            ttddruid = ""
            drugname = ""
            indications = []
            
            # Parse each line in the record
            for line in lines:
                if line.startswith("TTDDRUID"):
                    ttddruid = line.split("\t")[1].strip()
                elif line.startswith("DRUGNAME"):
                    drugname = line.split("\t")[1].strip()
                elif line.startswith("INDICATI"):
                    parts = line.split("\t")
                    # Extract indication fields
                    indication_disease = parts[1].strip()
                    indication_icd11 = parts[2].strip() if len(parts) > 2 else ""
                    indication_status = parts[3].strip() if len(parts) > 3 else ""
                    indications.append((indication_disease, indication_icd11, indication_status))
            
            # Write each parsed indication to the output file with an id
            for indication in indications:
                out_f.write(f'{id_counter},"{ttddruid}","{drugname}","{indication[0]}","{indication[1]}","{indication[2]}"\n')
                id_counter += 1  # Increment the id counter for each row


# Define input and output file paths
input_file = 'P1-05-Drug_disease_HEADER_REMOVED.txt'
output_file = 'dragan_indicators.csv'

# Run the parsing function
parse_srcdata(input_file, output_file)
print("Extracted indicators from TTD target text file - indicator .csv generated.")
