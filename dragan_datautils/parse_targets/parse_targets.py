# parse_targets: extract target data from TTD target text file
# output : .csv (id,id_target,id_unipro,name_target,name_gene,type_target,function_target)

def parse_data(file_path):
    data = []
    fields = ["TARGETID", "UNIPROID", "TARGNAME", "GENENAME", "TARGTYPE", "FUNCTION"]
    id_counter = 1  # Initialize the unique ID counter starting at 1

    # Open the file with utf-8 encoding
    with open(file_path, 'r', encoding='utf-8') as file:
        record = {}
        for line in file:
            line = line.strip()
            
            # Check for blank lines (indicating end of a record)
            if not line:
                if record:
                    # Add the record with the current ID to data and reset record
                    data.append([id_counter] + [record.get(field, "") for field in fields])
                    id_counter += 1
                    record = {}
                continue
            
            # Split line into parts
            parts = line.split(maxsplit=2)
            if len(parts) < 3:
                continue
            target_id, field, value = parts
            
            # Only capture necessary fields
            if field in fields:
                # Append value to field in case of multiline fields like FUNCTION
                if field in record:
                    record[field] += " " + value
                else:
                    record[field] = value
        
        # Append the last record if it exists
        if record:
            data.append([id_counter] + [record.get(field, "") for field in fields])

    # Write parsed data to output CSV file
    with open("dragan_targets.csv", "w", encoding='utf-8') as csvfile:
        # Write header with the specified fields
        csvfile.write("id,id_target,id_unipro,name_target,name_gene,type_target,function_target\n")
        
        # Write each row with id unquoted and other fields quoted
        for row in data:
            csvfile.write(f'{row[0]},"{row[1]}","{row[2]}","{row[3]}","{row[4]}","{row[5]}","{row[6]}"\n')

# Example usage
parse_data("P1-01-TTD_target_download_HEADER_REMOVED.txt")
print("Extracted target data from TTD target text file - target .csv generated.")
