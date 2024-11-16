# parse_drugs: extract drug data from TTD target text file
# output : .csv (id,id_target,id_drug,name_drug,clinicalstatus)

def parse_drug_data(file_path):
    data = []
    target_id = None
    id_counter = 1  # Initialize the unique ID counter starting at 1

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            
            # Check for blank lines (indicating end of a record set)
            if not line:
                target_id = None  # Reset target ID after each blank line
                continue
            
            # Split line into parts
            parts = line.split(maxsplit=2)
            if len(parts) < 3:
                continue
            
            # Assign parts for processing
            first_part, field, remaining_data = parts[0], parts[1], parts[2]
            
            # Capture TARGETID for DRUGINFO fields
            if field == "TARGETID":
                target_id = remaining_data
            
            # Process only DRUGINFO entries
            if field == "DRUGINFO" and target_id:
                drug_parts = remaining_data.split(maxsplit=2)
                if len(drug_parts) >= 3:
                    ttddruid, drugname, clinicalstatus = drug_parts[0], drug_parts[1], drug_parts[2]
                else:
                    # Handle cases where the clinical status might be missing or incomplete
                    ttddruid = drug_parts[0]
                    drugname = drug_parts[1] if len(drug_parts) > 1 else ""
                    clinicalstatus = ""

                # Add parsed drug info to data list, including unique id
                data.append([id_counter, target_id, ttddruid, drugname, clinicalstatus])
                id_counter += 1  # Increment the unique ID counter for each entry

    # Write parsed data to output CSV file
    with open("dragan_drugs.csv", "w", encoding='utf-8') as csvfile:
        # Write header with the specified fields
        csvfile.write("id,id_target,id_drug,name_drug,clinicalstatus\n")
        
        # Write each row with id unquoted and other fields quoted
        for row in data:
            line = f'{row[0]},"{row[1]}","{row[2]}","{row[3]}","{row[4]}"\n'
            csvfile.write(line)

# Example usage
parse_drug_data("P1-01-TTD_target_download_HEADER_REMOVED.txt")
print("Extracted drug data from TTD target text file - drug .csv generated.")

